package com.hood.robin.insta_clone;

import android.app.ProgressDialog;
import android.content.Intent;
import android.support.annotation.NonNull;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.AuthResult;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

import java.util.Objects;

public class LoginActivity extends AppCompatActivity {


    private Button loginButton, phoneLoginButton;
    private EditText UserEmail, UserPassword;
    private TextView NeedNewAccount, ForgetPasswordLink;

    private ProgressDialog loadingBar;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.activity_login);

        InitializeField();



    }




    private void InitializeField(){

        loginButton = (Button)findViewById(R.id.login_button);
        phoneLoginButton = (Button)findViewById(R.id.phone_login_button);
        UserEmail = (EditText)findViewById(R.id.login_email);
        UserPassword = (EditText)findViewById(R.id.login_password);
        NeedNewAccount = (TextView)findViewById(R.id.need_new_account);
        ForgetPasswordLink = (TextView)findViewById(R.id.forget_password_link);
        loadingBar = new ProgressDialog(this);

    }







}
