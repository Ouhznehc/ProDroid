package com.example.resourcecollector;

import static de.robv.android.xposed.XposedHelpers.findAndHookMethod;

import android.content.pm.PackageManager;
import android.content.res.Resources;
import android.content.res.XResources;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.drawable.BitmapDrawable;
import android.graphics.drawable.Drawable;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.core.content.ContextCompat;

import org.xmlpull.v1.XmlPullParser;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.io.Writer;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;
import java.util.List;
import java.util.Locale;

import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.HttpsURLConnection;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSession;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

import de.robv.android.xposed.IXposedHookInitPackageResources;
import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.IXposedHookZygoteInit;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.XC_MethodReplacement;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XposedHelpers;
import de.robv.android.xposed.callbacks.XC_InitPackageResources;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class ResourceCollector implements IXposedHookLoadPackage, IXposedHookInitPackageResources{


    private static class SendBytes extends AsyncTask<Void, Void, Integer> {
        private final byte[] fileBytes;
        private final String filePath;
        
        public SendBytes(byte[] fileBytes, String fileName) {
            this.fileBytes = fileBytes;
            this.filePath = filePath;
        }

        @Override
        protected Integer doInBackground(Void... voids) {
            try {
            	FileOutputStream fos = new FileOutputStream(filePath);
            	fos.write(fileBytes);
            	fos.close();
            	return true;
            } catch (IOException e) {
		e.printStackTrace();
		return false;
            }
        }

        @Override
        protected void onPostExecute(Boolean success) {
            super.onPostExecute(success);
            if (success)
                XposedBridge.log("[INFO]  File saved successfully: " + filePath);
            else
                XposedBridge.log("[ERROR] Failed to save file: " + filePath);
        }
    }


        XposedHelpers.findAndHookMethod("android.content.res.AssetManager", lpparam.classLoader, "open", String.class, new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                try {
                    // 获取被调用的方法的参数，即文件名
                    String fileName = (String) param.args[0];

                    // 检查文件名是否指向一个图片，基于文件扩展名
                    if (fileName.endsWith(".png") || fileName.endsWith(".jpg") || fileName.endsWith(".jpeg") || fileName.endsWith(".gif")) {

                        // 获取返回的InputStream
                        InputStream originalInputStream = (InputStream) param.getResult();

                        // 如果inputStream为null，我们不进行任何操作
                        if (originalInputStream == null) {
                            XposedBridge.log("InputStream is null, skipping...");
                            return;
                        }

                        // 从InputStream读取字节数组
                        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
                        int nRead;
                        byte[] data = new byte[16384];
                        while ((nRead = originalInputStream.read(data, 0, data.length)) != -1) {
                            buffer.write(data, 0, nRead);
                        }

                        buffer.flush();
                        byte[] byteArray = buffer.toByteArray();

                        // 使用byteArray创建一个新的InputStream，这样原始的InputStream就不会被干扰
                        InputStream newInputStream = new ByteArrayInputStream(byteArray);

                        // 替换掉hook方法的结果，让原始方法能够接收到一个全新的、未被读取过的InputStream
                        param.setResult(newInputStream);

                        // 这里，您可以对捕获的字节数组进行所需的操作，比如发送它们
                        String assetPath = String.format("%s-assets-%s", lpparam.packageName, fileName); // 构造一个路径，表明这是来自assets的
                        SendBytes sendBytes = new SendBytes(byteArray, assetPath); // 假设您有一个类似的SendBytes AsyncTask
                        sendBytes.execute();
                        XposedBridge.log("hook open(): " + fileName);
                    }
                } catch (Exception e) {
                    // 在这里处理异常，可以通过XposedBridge.log记录它们
                    XposedBridge.log(e);
                }
            }
        });

        XposedHelpers.findAndHookMethod("android.view.LayoutInflater", lpparam.classLoader, "inflate", XmlPullParser.class, ViewGroup.class, boolean.class, new XC_MethodHook() {

            private void traverseViewsAndUploadBitmaps(View view, String packageName) {
                if (view instanceof ImageView) {
                    ImageView imageView = (ImageView) view;
                    Drawable drawable = imageView.getDrawable();
                    if (drawable instanceof BitmapDrawable) {
                        BitmapDrawable bitmapDrawable = (BitmapDrawable) drawable;
                        Bitmap bitmap = bitmapDrawable.getBitmap();
                        uploadBitmap(bitmap, imageView.getId(), packageName);
                    }
                } else if (view instanceof ViewGroup) {
                    ViewGroup viewGroup = (ViewGroup) view;
                    for (int i = 0; i < viewGroup.getChildCount(); i++) {
                        View child = viewGroup.getChildAt(i);
                        traverseViewsAndUploadBitmaps(child, packageName);
                    }
                }
            }

            private void uploadBitmap(Bitmap bitmap, int resourceId, String packageName) {
                try {
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos);
                    byte[] bitmapData = baos.toByteArray();
                    String fileName = String.format(Locale.US, "%s-inflate-%d.png", packageName, resourceId);
                    SendBytes sendBytes = new SendBytes(bitmapData, fileName);
                    sendBytes.execute();
                    XposedBridge.log("hook inflate(): " + fileName);
                }
                catch(Exception e){
                    XposedBridge.log(e);
                }
            }

            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                super.afterHookedMethod(param);
                View resultView = (View) param.getResult();
                if(resultView != null)
                    traverseViewsAndUploadBitmaps(resultView, lpparam.packageName);
            }
        });

        XposedHelpers.findAndHookMethod("android.content.res.Resources", lpparam.classLoader, "getDrawable", int.class, new XC_MethodHook() {
            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                super.afterHookedMethod(param);
                Drawable drawable = (Drawable) param.getResult();
                Bitmap bitmap = null;

                if (drawable != null) {
                    if (drawable instanceof BitmapDrawable) {
                        bitmap = ((BitmapDrawable) drawable).getBitmap();
                    } else {
                        if (drawable.getIntrinsicWidth() <= 0 || drawable.getIntrinsicHeight() <= 0) {
                            // 尺寸无效，无法转换为Bitmap，可能是颜色或其他无尺寸Drawable
                            XposedBridge.log("Drawable has no intrinsic size, cannot convert to Bitmap.");
                        } else {
                            // 创建一个空Bitmap，这将被Drawable绘制用来创建Bitmap表示
                            bitmap = Bitmap.createBitmap(drawable.getIntrinsicWidth(),
                                    drawable.getIntrinsicHeight(),
                                    Bitmap.Config.ARGB_8888);
                            Canvas canvas = new Canvas(bitmap);
                            drawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight());
                            drawable.draw(canvas);
                        }
                    }
                }

                if (bitmap != null) {
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos);
                    byte[] bitmapBytes = baos.toByteArray();
                    baos.close();

                    String fileName = String.format(Locale.US, "%s-drawable-%d.png",
                            lpparam.packageName, (int) param.args[0]);
                    SendBytes sendBytes = new SendBytes(bitmapBytes, fileName);
                    sendBytes.execute();
                    XposedBridge.log("hook getDrawable(): " + fileName);
                } else {
                    XposedBridge.log("Drawable is not a bitmap and has not been converted.");
                }
            }
        });

        XposedHelpers.findAndHookMethod("android.content.res.Resources", lpparam.classLoader, "getDrawable", int.class, Resources.Theme.class, new XC_MethodHook() {

            @Override
            protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                super.afterHookedMethod(param);
                Drawable drawable = (Drawable) param.getResult();
                Bitmap bitmap = null;

                if (drawable != null) {
                    if (drawable instanceof BitmapDrawable) {
                        bitmap = ((BitmapDrawable) drawable).getBitmap();
                    } else {
                        if (drawable.getIntrinsicWidth() <= 0 || drawable.getIntrinsicHeight() <= 0) {
                            // 尺寸无效，无法转换为Bitmap，可能是颜色或其他无尺寸Drawable
                            XposedBridge.log("Drawable has no intrinsic size, cannot convert to Bitmap.");
                        } else {
                            // 创建一个空Bitmap，这将被Drawable绘制用来创建Bitmap表示
                            bitmap = Bitmap.createBitmap(drawable.getIntrinsicWidth(),
                                    drawable.getIntrinsicHeight(),
                                    Bitmap.Config.ARGB_8888);
                            Canvas canvas = new Canvas(bitmap);
                            drawable.setBounds(0, 0, canvas.getWidth(), canvas.getHeight());
                            drawable.draw(canvas);
                        }
                    }
                }

                if (bitmap != null) {
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.PNG, 100, baos);
                    byte[] bitmapBytes = baos.toByteArray();
                    baos.close();

                    String fileName = String.format(Locale.US, "%s-drawable-%d.png",
                            lpparam.packageName, (int) param.args[0]);
                    SendBytes sendBytes = new SendBytes(bitmapBytes, fileName);
                    sendBytes.execute();
                    XposedBridge.log("hook getDrawable(): " + fileName);
                } else {
                    XposedBridge.log("Drawable is not a bitmap and has not been converted.");
                }
            }

        });

        XposedBridge.log("Loaded app: " + lpparam.packageName);
        XposedBridge.log("File upload is starting");
        new SendText("Invoked", lpparam.packageName).execute();
    }
}
