package com.hood.robin.insta_clone;

import android.app.Activity;

import android.content.Context;
import android.support.annotation.NonNull;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.TextView;
import  android.R.id;
import java.util.Objects;

import static com.hood.robin.insta_clone.R.layout.list_single;


public class CustomList extends ArrayAdapter<String>{

    private final ContactsFragment context;
    private final String[] web;
    private final Integer[] imageId;

    CustomList(ContactsFragment context,
               String[] web, Integer[] imageId) {
        super( context.getActivity(),list_single,web);
        // super(Objects.requireNonNull(ContactsFragment), list_single, web);
        //this.context = (ContactsFragment) getContext();
        this.context = context;
        this.web = web;
        this.imageId = imageId;

    }
    @Override
    public View getView(int position, View view, ViewGroup parent) {
        LayoutInflater inflater = context.getLayoutInflater();
        View rowView = inflater.inflate(list_single, null, true);
        TextView txtTitle = (TextView) rowView.findViewById(R.id.text_description);

        ImageView imageView = (ImageView) rowView.findViewById(R.id.img);
        txtTitle.setText(web[position]);

        imageView.setImageResource(imageId[position]);
        return rowView;
    }



}
