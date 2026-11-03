package org.lanonapp.alpha;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.IOException;
import java.io.InputStream;

/** Minimal pre-alpha offline-first WebView shell; no privileged JS bridge. */
public final class MainActivity extends Activity {
    private WebView web;
    private static final String ORIGIN="appassets.androidplatform.net";
    @Override public void onCreate(Bundle b) {
        super.onCreate(b);
        web=new WebView(this);
        web.setBackgroundColor(0xfff4f5f0);
        WebSettings s=web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        web.setWebViewClient(new WebViewClient(){
            @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest request){
                Uri url=request.getUrl();
                if (!"https".equals(url.getScheme()) || !ORIGIN.equals(url.getHost())) return null;
                String path=url.getPath();
                if(path==null || !path.startsWith("/app/"))return forbidden();
                String name=path.substring(5);
                if(name.isEmpty())name="index.html";
                // Reject traversal and unexpected filenames before accessing APK assets.
                if(name.contains("..")||name.startsWith("/")||name.contains("\\"))return forbidden();
                String mime=name.endsWith(".html")?"text/html":name.endsWith(".js")?"text/javascript":name.endsWith(".css")?"text/css":name.endsWith(".json")||name.endsWith(".webmanifest")?"application/json":name.endsWith(".png")?"image/png":"text/plain";
                try {InputStream in=getAssets().open("web/"+name);return new WebResourceResponse(mime,"UTF-8",in);}
                catch(IOException ex){return forbidden();}
            }
            private WebResourceResponse forbidden(){return new WebResourceResponse("text/plain","UTF-8",new java.io.ByteArrayInputStream(new byte[0]));}
            @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest request){
                Uri uri=request.getUrl();
                if(ORIGIN.equals(uri.getHost()))return false;
                if(request.isForMainFrame() && "https".equals(uri.getScheme())) {
                    try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception ignored){}
                    return true;
                }
                return request.isForMainFrame(); // embedded media remains governed by provider.
            }
        });
        setContentView(web);
        web.loadUrl("https://"+ORIGIN+"/app/index.html");
    }
    @Override @SuppressWarnings("deprecation") public void onBackPressed(){
        if(web!=null&&web.canGoBack())web.goBack();else super.onBackPressed();
    }
    @Override protected void onDestroy(){if(web!=null){web.destroy();web=null;}super.onDestroy();}
}
