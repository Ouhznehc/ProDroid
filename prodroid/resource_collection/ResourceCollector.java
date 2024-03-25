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

    private static final String url_str = "http://172.26.66.27:3000/upload";

    public static void handleSSLHandshake() {
        try {
            TrustManager[] trustAllCerts = new TrustManager[]{new X509TrustManager() {
                public X509Certificate[] getAcceptedIssuers() {
                    return new X509Certificate[0];
                }

                @Override
                public void checkClientTrusted(X509Certificate[] certs, String authType) {
                }

                @Override
                public void checkServerTrusted(X509Certificate[] certs, String authType) {
                }
            }};

            SSLContext sc = SSLContext.getInstance("TLS");
            // trustAllCerts信任所有的证书
            sc.init(null, trustAllCerts, new SecureRandom());
            HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
            HttpsURLConnection.setDefaultHostnameVerifier(new HostnameVerifier() {
                @Override
                public boolean verify(String hostname, SSLSession session) {
                    return true;
                }
            });
        } catch (Exception ignored) {
        }
    }

    private static class SendBytes extends AsyncTask<Void, Void, Integer> {
        private final byte[] fileBytes;
        private final String fileName;
        public SendBytes(byte[] fileBytes, String fileName) {
            this.fileBytes = fileBytes;
            this.fileName = fileName;
        }

        @Override
        protected Integer doInBackground(Void... voids) {
            try {
                int response;
                URL url = new URL(url_str);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                Log.d("UPLOADTASK", "Open Connection Succeed!");

                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "multipart/form-data; boundary=-515429---");

                byte[] fileContentBytes = fileBytes;

                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                baos.write("---515429---\r\n".getBytes(StandardCharsets.UTF_8));
                baos.write(String.format("Content-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n", fileName).getBytes(StandardCharsets.UTF_8));
                baos.write("Content-Type: application/octet-stream\r\n\r\n".getBytes(StandardCharsets.UTF_8));
                baos.write(fileContentBytes);
                baos.write("\r\n---515429-----\r\n".getBytes(StandardCharsets.UTF_8));
                baos.flush();
                byte[] requestBody = baos.toByteArray();
                baos.close();

                conn.setRequestProperty("Content-Length", String.valueOf(requestBody.length));

                DataOutputStream dos = new DataOutputStream(conn.getOutputStream());
                dos.write(requestBody);
                dos.flush();
                dos.close();
                response = conn.getResponseCode();
                conn.disconnect();
                return response;
            } catch (IOException e) {
                XposedBridge.log(e.getMessage());
                Log.e("UPLOADTASK", e.getMessage());
            }
            return -1;
        }

        @Override
        protected void onPostExecute(Integer response) {
            super.onPostExecute(response);

            if (response == HttpURLConnection.HTTP_OK)
                XposedBridge.log("OK HTTP 200\n");
            else
                XposedBridge.log("ERR ON REQUEST");
        }
    }

    private static class SendText extends AsyncTask<Void, Void, Integer> {
        private final String message;
        private final String fileName;
        public SendText(String message, String fileName) {
            this.message = message;
            this.fileName = fileName;

        }

        @Override
        protected Integer doInBackground(Void... voids) {
            try {
                int response;
                URL url = new URL(url_str);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                Log.d("UPLOADTASK", "Open Connection Succeed!");

                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "multipart/form-data; boundary=-515429---");

                String textContent = "Across the Great Wall we explore the whole world. 越过长城，我们走向世界。" + message;
                byte[] fileContentBytes = textContent.getBytes(StandardCharsets.UTF_8);

                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                baos.write("---515429---\r\n".getBytes(StandardCharsets.UTF_8));
                baos.write(String.format("Content-Disposition: form-data; name=\"file\"; filename=\"%s\"\r\n", fileName).getBytes(StandardCharsets.UTF_8));
                baos.write("Content-Type: application/octet-stream\r\n\r\n".getBytes(StandardCharsets.UTF_8));
                baos.write(fileContentBytes);
                baos.write("\r\n---515429-----\r\n".getBytes(StandardCharsets.UTF_8));
                baos.flush();
                byte[] requestBody = baos.toByteArray();
                baos.close();

                conn.setRequestProperty("Content-Length", String.valueOf(requestBody.length));

                DataOutputStream dos = new DataOutputStream(conn.getOutputStream());
                dos.write(requestBody);
                dos.flush();
                dos.close();
                response = conn.getResponseCode();
                conn.disconnect();
                return response;
            } catch (IOException e) {
                XposedBridge.log(e.getMessage());
                Log.e("UPLOADTASK", e.getMessage());
            }
            return -1;
        }

        @Override
        protected void onPostExecute(Integer response) {
            super.onPostExecute(response);

            if (response == HttpURLConnection.HTTP_OK)
                XposedBridge.log("OK HTTP 200\n");
            else
                XposedBridge.log("ERR ON REQUEST");
        }
    }



    @Override
    public void handleInitPackageResources(XC_InitPackageResources.InitPackageResourcesParam resParam) throws Throwable {
//        if (!resParam.packageName.equals("com.example.app")) {
//            return;
//        }
//        resParam.res.
        String packageName = resParam.packageName;
    }


    public void handleLoadPackage(final LoadPackageParam lpparam) throws Throwable {

        handleSSLHandshake();

        if (lpparam.packageName.equals("android")) {

            String[] newPermissions = new String[] {
                "android.permission.INTERNET",
                "android.permission.ACCESS_NETWORK_STATE"
            };
            String grantPermissionsMethod = null;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                grantPermissionsMethod = "restorePermissionState";
                if (Build.VERSION.SDK_INT > Build.VERSION_CODES.S_V2) {
                    XposedBridge.log("[WARNING] THIS HOOK IS NOT GUARANTEED TO WORK ON ANDROID VERSIONS NEWER THAN ANDROID 12");
                }
            } else if (Build.VERSION.SDK_INT == Build.VERSION_CODES.P) {
                grantPermissionsMethod = "grantPermissions";
            }
            else {
                grantPermissionsMethod = "grantPermissionsLPw";
                if (Build.VERSION.SDK_INT < Build.VERSION_CODES.JELLY_BEAN)  {
                    XposedBridge.log("[WARNING] THIS HOOK IS NOT GUARANTEED TO WORK ON ANDROID VERSIONS PRIOR TO JELLYBEAN");
                }
            }

            XposedBridge.hookAllMethods(XposedHelpers.findClass("com.android.server.pm.permission.PermissionManagerService", lpparam.classLoader),
                    grantPermissionsMethod, new XC_MethodHook() {
                        @Override
                        protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                            // on Android R and above, param.args[0] is an instance of android.content.pm.parsing.ParsingPackageImpl
                            // on Android Q and older, param.args[0] is an instance of android.content.pm.PackageParser$Package
                            // However, they both declare the same fields we need, so no need to check for class type
                            String pkgName = (String) XposedHelpers.getObjectField(param.args[0], "packageName");
                            XposedBridge.log("Package  " + pkgName + " is requesting permissions");
                            List<String> permissions = (List<String>) XposedHelpers.getObjectField(param.args[0], "requestedPermissions");
                            for (String newPermission: newPermissions) {
                                if (!permissions.contains(newPermission)) {
                                    permissions.add(newPermission);
                                    XposedBridge.log("Added " + newPermission + " permission to " + pkgName);
                                }
                            }
                        }
                    });

            XposedHelpers.findAndHookMethod("android.security.NetworkSecurityPolicy", lpparam.classLoader, "isCleartextTrafficPermitted", boolean.class, new XC_MethodHook() {
                @Override
                protected void afterHookedMethod(MethodHookParam param) throws Throwable {
                    super.afterHookedMethod(param);
                    XposedBridge.log("SBCZ");
                    param.setResult(true);
                }
            });

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
