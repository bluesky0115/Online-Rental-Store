package com.hood.robin.insta_clone;


import android.annotation.SuppressLint;
import android.content.Intent;

import android.graphics.Bitmap;
import android.net.http.SslError;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.widget.EditText;
import android.widget.ListView;

import java.util.ArrayList;
import java.util.Objects;

import android.R.*;
import android.widget.Toast;
import android.view.KeyEvent;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import static com.hood.robin.insta_clone.R.string.tag;

/**
 * A simple {@link Fragment} subclass.
 */
public class ChatsFragment extends Fragment {


    private WebView webView = null;


    public ChatsFragment() {
        // Required empty public constructor
    }


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View myView = inflater.inflate(R.layout.fragment_chats, container,false);


       this.webView = (WebView)myView.findViewById(R.id.webview);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient());

        webView.getSettings().setDomStorageEnabled(true);

        String Tag = "webview";
        Log.i(Tag,"http://tutorials.jenkov.com");

        webView.loadUrl("http://smgroup16.pythonanywhere.com/ors/login");
        webView.setWebViewClient(new MyWebViewClient());
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);

        // webView.clearView();
        //webView.measure(100, 100);
        //webView.getSettings().setUseWideViewPort(true);
        //webView.getSettings().setLoadWithOverviewMode(true);


       // WebViewClientImpl webViewClient = new WebViewClientImpl(this);

       // webView.setWebViewClient(webViewClient);
       // webView.setWebChromeClient(new WebChromeClient());

        //webView.loadData("<html><body>Hello, world!</body></html>", "text/html", "UTF-8");

        return myView;


    }
    private class MyWebViewClient extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, String url) {
            webView.loadUrl(url);
            return true;
        }

        @Override
        public void onReceivedSslError(WebView view, SslErrorHandler handler,
                                       SslError error) {
            super.onReceivedSslError(view, handler, error);
            handler.proceed();
        }
    }



}
