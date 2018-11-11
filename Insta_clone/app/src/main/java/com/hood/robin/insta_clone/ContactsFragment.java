package com.hood.robin.insta_clone;


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
public class ContactsFragment extends Fragment {


    private WebView webView = null;




    public ContactsFragment() {
        // Required empty public constructor
    }




    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragment_contacts, container, false);
        // Inflate the layout for this fragment
        this.webView = (WebView)v.findViewById(R.id.webview_profile);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient());

        webView.getSettings().setDomStorageEnabled(true);

        String Tag = "webview";
        Log.i(Tag,"http://tutorials.jenkov.com");

        webView.loadUrl("http://smgroup16.pythonanywhere.com/ors/profile");
        webView.setWebViewClient(new ContactsFragment.MyWebViewClient());
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);



        return v;
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
