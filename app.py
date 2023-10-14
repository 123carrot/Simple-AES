import os
import time

import numpy as np
from flask import Flask, render_template, request, jsonify, send_file

import SimpleAes

app = Flask(__name__)
workfile = ""
readfile = ''
storedir = ''


@app.route('/')
def eightbits():
    return render_template("index.html")


@app.route('/str')
def strbits():
    return render_template("str.html")


@app.route('/file')
def filebits():
    return render_template("file.html")


@app.route('/slove')
def solve():
    return render_template("slove.html")


@app.route('/file/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        if file.filename.endswith('.txt'):
            global workfile
            workfile = file.filename
            print(workfile)
            filename = os.path.join("upload", file.filename)  # "upload" 是目标文件夹
            file.save(filename)
            return jsonify({'success': True, 'message': 'File uploaded successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    else:
        return 'No file uploaded', 400


@app.route('/index/start', methods=['POST'])
def start():
    data = request.get_json()
    mingwen = data.get('mingwen')
    miyao = data.get('miyao')
    option = data.get('options')
    miyao = np.array(list(miyao)).astype(int)
    # print(miyao)
    mingwen = np.array(list(mingwen)).astype(int)
    # print(option)
    if option == 'S-AES':
        result = SimpleAes.encode(miyao, mingwen)
    elif option == '2-AES':
        result = SimpleAes.doubleEncode(miyao,mingwen)
    elif option == '3-AES':
        result = SimpleAes.tripleEncode(miyao, mingwen)
    result = ''.join(c for c in result.astype(str))
    return jsonify({'result': result})


@app.route('/index/dec8', methods=['POST'])
def dec8():
    data = request.get_json()
    mingwen = data.get('mingwen')
    miyao = data.get('miyao')
    option = data.get('options')
    miyao = np.array(list(miyao)).astype(int)
    # print(miyao)
    mingwen = np.array(list(mingwen)).astype(int)
    if option == 'S-AES':
        result = SimpleAes.decode(miyao, mingwen)
    elif option == '2-AES':
        result = SimpleAes.doubleDecode(miyao, mingwen)
    elif option == '3-AES':
        result = SimpleAes.tripleDecode(miyao, mingwen)
    result = ''.join(c for c in result.astype(str))
    return jsonify({'result': result})


# 字符串加密
@app.route('/str/str_encode', methods=['POST'])
def str_encode():
    data = request.get_json()
    mingwen = data.get('str_mingwen')
    miyao = data.get('str_miyao')
    opt = data.get('option')
    miyao = np.array(list(miyao)).astype(int)
    # print(miyao)
    if opt == 'CBC':
        result = SimpleAes.encodeCBCString(miyao, mingwen)
    else:
        result = SimpleAes.encode_str(miyao, mingwen)
    # print(result)
    return jsonify({'result': result})


# 字符串解密
@app.route('/str/str_decode', methods=['POST'])
def str_decode():
    data = request.get_json()
    mingwen = data.get('str_mingwen')
    miyao = data.get('str_miyao')
    opt = data.get('option')
    miyao = np.array(list(miyao)).astype(int)
    if opt == 'CBC':
        result = SimpleAes.decodeCBCString(miyao, mingwen)
    else:
        result = SimpleAes.decode_str(miyao, mingwen)
    return jsonify({'result': result})


# 文件加密
@app.route('/file/file_encode', methods=['POST'])
def file_encode():
    data = request.get_json()
    miyao = data.get('file_miyao')
    miyao = np.array(list(miyao)).astype(int)
    global workfile
    global storedir
    global readfile
    readfile = "./upload/" + workfile
    storedir = "./result/" + workfile
    with open(storedir, 'w', encoding='utf-16') as f:
        with open(readfile, 'r') as file:
            for line in file:
                temp = SimpleAes.encode_str(miyao, line)
                f.write(temp)
    result = ''
    return jsonify({'result': result})


@app.route('/file/file_decode', methods=['POST'])
def file_decode():
    data = request.get_json()
    miyao = data.get('file_miyao')
    miyao = np.array(list(miyao)).astype(int)
    global workfile
    global storedir
    global readfile
    readfile = "./upload/" + workfile
    storedir = "./result/" + workfile
    with open(storedir, 'w') as f:
        with open(readfile, 'r', encoding='utf-16') as file:
            for line in file:
                temp = SimpleAes.decode_str(miyao, line)
                f.write(temp)
    result = ''
    return jsonify({'result': result})


@app.route('/file/download')
def download():
    global storedir
    file_path = storedir
    return send_file(file_path, as_attachment=True, download_name=workfile)


@app.route('/startslove', methods=['POST'])
def startslove():
    stime = time.time()
    data = request.get_json()
    mingwen = data.get('mingwen')
    miwen = data.get('miwen')
    miwen = np.array(list(miwen)).astype(int)
    mingwen = np.array(list(mingwen)).astype(int)
    resultarr = SimpleAes.brute_force_sdes(miwen, mingwen)
    result = ''
    if len(resultarr) > 5:
        resultarr = resultarr[0:5]
        result += '可能的总密钥大于五个，只展示前五条\n'
    for arr in resultarr:
        temp = ''.join(c for c in arr.astype(str))
        result += temp
        result += '\n'
    etime = time.time()
    print("破解用时 %.4f 秒" % (etime - stime))
    return jsonify({'result': result})


if __name__ == '__main__':
    app.run()
