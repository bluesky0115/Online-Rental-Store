package com.hood.robin.insta_clone;

import android.app.Activity;
import android.content.Context;
import android.graphics.ColorSpace;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.TextView;

import java.util.ArrayList;

public class CustomAdapter extends BaseAdapter {

    Context context;
    ArrayList<Model> itemModelList;



    public CustomAdapter(Context applicationContext, ArrayList<Model> itemModelList) {
    }

    @Override
    public int getCount() {
        try{
        return itemModelList.size();
        }
        catch(Exception e){
            return 0;
        }
    }

    @Override
    public Object getItem(int i) {
        return itemModelList.get(i);

    }

    @Override
    public long getItemId(int i) {
        return i;
    }

    @Override
    public View getView(final int i, View view, ViewGroup viewGroup) {
        View convertView = null;
        if (convertView == null) {
            LayoutInflater mInflater = (LayoutInflater) context
                    .getSystemService(Activity.LAYOUT_INFLATER_SERVICE);
            convertView = mInflater.inflate(R.layout.item, null);
            TextView tvName = (TextView) convertView.findViewById(R.id.tvName);
            ImageView imgRemove = (ImageView) convertView.findViewById(R.id.imgRemove);
            Model m = itemModelList.get(i);
            tvName.setText("Hello");
            // click listiner for remove button
            imgRemove.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    itemModelList.remove(i);
                    notifyDataSetChanged();
                }
            });
        }
        return convertView;
    }
}
