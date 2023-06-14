package com.chaquo.myapplication

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.lang.StringBuilder

class MainActivity2 : AppCompatActivity() {
    private var module: PyObject? = null
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
//        Thread(Runnable {
//            val py = Python.getInstance()
//            module = py.getModule("data")
//            runOnUiThread(Runnable {
//                Toast.makeText(this, "Init success", Toast.LENGTH_LONG).show()
//            })
//        }).start()
        val py = Python.getInstance()
        module = py.getModule("data")
        val builder=StringBuilder(readFileFromAssets(this,"demo.txt"))
        val bytes = module?.callAttr(
            "load_recommender",builder.toString()
        ).toString()
        Toast.makeText(this, bytes, Toast.LENGTH_LONG).show()
        Log.d("TAG", "onCreate Prompt : $bytes")

        findViewById<Button>(R.id.button).setOnClickListener {
            val edt=findViewById(R.id.etX) as EditText
            val bytes = module?.callAttr("generate_answer",edt.text.toString().trim()).toString()
            Log.d("TAG", "onCreate Prompt : $bytes")
        }
    }

    fun readFileFromAssets(context: Context, fileName: String): String {
        val rs = StringBuilder()
        try {
            BufferedReader(InputStreamReader(context.assets.open(fileName))).use { reader ->
                var mLine: String?
                while (reader.readLine().also { mLine = it } != null) {
                    //process line
                    rs.append(mLine)
                }
            }
        } catch (e: IOException) {
            //log the exception
        }
        //log the exception
        return rs.toString()
    }

}