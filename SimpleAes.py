import numpy as np


# 构造状态矩阵 输入16位0/1数组
def stateMatConstruct(arr):
    arr = np.array(arr)
    S00 = arr[0:4]
    S10 = arr[4:8]
    S01 = arr[8:12]
    S11 = arr[12:16]
    return [S00, S01, S10, S11]


# 状态矩阵析构，转换回数组
def stateMatDestorey(mat):
    return np.concatenate([mat[0], mat[2], mat[1], mat[3]])


# 密钥加 输入16bit与密钥
def addKey(arr, key):
    arr = np.array(arr)
    key = np.array(key)
    res = np.bitwise_xor(arr, key)
    return res


# 半字节替代 S盒
def halfByteSubstitude(arr):
    indexDic = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
    SBox = [
        [np.array([1, 0, 0, 1]), np.array([0, 1, 0, 0]), np.array([1, 0, 1, 0]), np.array([1, 0, 1, 1])],
        [np.array([1, 1, 0, 1]), np.array([0, 0, 0, 1]), np.array([1, 0, 0, 0]), np.array([0, 1, 0, 1])],
        [np.array([0, 1, 1, 0]), np.array([0, 0, 1, 0]), np.array([0, 0, 0, 0]), np.array([0, 0, 1, 1])],
        [np.array([1, 1, 0, 0]), np.array([1, 1, 1, 0]), np.array([1, 1, 1, 1]), np.array([0, 1, 1, 1])]
    ]
    mat = stateMatConstruct(arr)
    for i in range(4):
        mat[i] = SBox[indexDic[tuple(mat[i][0:2])]][indexDic[tuple(mat[i][2:4])]]
    return stateMatDestorey(mat)


def inverseHalfByteSubstitude(arr):
    indexDic = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
    SBox = [
        [np.array([1, 0, 1, 0]), np.array([0, 1, 0, 1]), np.array([1, 0, 0, 1]), np.array([1, 0, 1, 1])],
        [np.array([0, 0, 0, 1]), np.array([0, 1, 1, 1]), np.array([1, 0, 0, 0]), np.array([1, 1, 1, 1])],
        [np.array([0, 1, 1, 0]), np.array([0, 0, 0, 0]), np.array([0, 0, 1, 0]), np.array([0, 0, 1, 1])],
        [np.array([1, 1, 0, 0]), np.array([0, 1, 0, 0]), np.array([1, 1, 0, 1]), np.array([1, 1, 1, 0])]
    ]
    mat = stateMatConstruct(arr)
    for i in range(4):
        mat[i] = SBox[indexDic[tuple(mat[i][0:2])]][indexDic[tuple(mat[i][2:4])]]
    return stateMatDestorey(mat)


# 行位移
def rowShift(arr):
    S00, S01, S10, S11 = stateMatConstruct(arr)
    mat = [S00, S01, S11, S10]
    return stateMatDestorey(mat)


# 有限域乘法
def mulGF(a, b):
    # 不可约多项式: p(x) = x^4 + x + 1
    irreducible = 0b10011
    # 正常多项式乘法
    result = 0
    for i in range(4):
        if (b >> i) & 1:
            result ^= a << i
    # 模不可约多项式
    for i in range(7, 3, -1):
        if (result >> i) & 1:
            result ^= irreducible << (i - 4)
    return result & 0b1111


# 有限域矩阵乘法
def mulGFMat(mat1, mat2):
    result = [[0] * 2 for _ in range(2)]
    for i in range(2):  # 修改为2
        for j in range(2):  # 修改为2
            sum = 0
            for k in range(2):  # 修改为2
                sum ^= mulGF(int(''.join(map(str, mat1[i][k])), 2), int(''.join(map(str, mat2[k][j])), 2))
            result[i][j] = np.array(list(map(int, format(sum, '04b'))))
    return result


# 列混淆
def columnMix(arr):
    mixMat = [
        [np.array([0, 0, 0, 1]), np.array([0, 1, 0, 0])],
        [np.array([0, 1, 0, 0]), np.array([0, 0, 0, 1])],
    ]
    mat = stateMatConstruct(arr)
    mat = [
        [mat[0], mat[1]],
        [mat[2], mat[3]]
    ]
    result = mulGFMat(mixMat, mat)
    K = [item for sublist in result for item in sublist]
    return stateMatDestorey(K)


# 逆列混淆
def inverseColumnMix(arr):
    mixMat = [
        [np.array([1, 0, 0, 1]), np.array([0, 0, 1, 0])],
        [np.array([0, 0, 1, 0]), np.array([1, 0, 0, 1])],
    ]
    mat = stateMatConstruct(arr)
    mat = [
        [mat[0], mat[1]],
        [mat[2], mat[3]]
    ]
    result = mulGFMat(mixMat, mat)
    K = [item for sublist in result for item in sublist]
    return stateMatDestorey(K)


# g函数
def functionG(w, RCON):
    n0 = w[0:4]
    n1 = w[4:8]
    indexDic = {(0, 0): 0, (0, 1): 1, (1, 0): 2, (1, 1): 3}
    SBox = [
        [np.array([1, 0, 0, 1]), np.array([0, 1, 0, 0]), np.array([1, 0, 1, 0]), np.array([1, 0, 1, 1])],
        [np.array([1, 1, 0, 1]), np.array([0, 0, 0, 1]), np.array([1, 0, 0, 0]), np.array([0, 1, 0, 1])],
        [np.array([0, 1, 1, 0]), np.array([0, 0, 1, 0]), np.array([0, 0, 0, 0]), np.array([0, 0, 1, 1])],
        [np.array([1, 1, 0, 0]), np.array([1, 1, 1, 0]), np.array([1, 1, 1, 1]), np.array([0, 1, 1, 1])]
    ]
    n0 = SBox[indexDic[tuple(n0[0:2])]][indexDic[tuple(n0[2:4])]]
    n1 = SBox[indexDic[tuple(n1[0:2])]][indexDic[tuple(n1[2:4])]]
    w0 = np.concatenate([n1, n0])
    return np.bitwise_xor(w0, RCON)


# 生成密钥 密钥扩展
def generate_key(key):
    w0 = key[0:8]
    w1 = key[8:16]
    RCON1 = np.array([1, 0, 0, 0, 0, 0, 0, 0])
    RCON2 = np.array([0, 0, 1, 1, 0, 0, 0, 0])
    w2 = np.bitwise_xor(w0, functionG(w1, RCON1))
    w3 = np.bitwise_xor(w2, w1)
    w4 = np.bitwise_xor(w2, functionG(w3, RCON2))
    w5 = np.bitwise_xor(w4, w3)
    return np.concatenate([w0, w1]), np.concatenate([w2, w3]), np.concatenate([w4, w5])


# 加密算法
def encode(key, content):
    k1, k2, k3 = generate_key(key)
    content = np.array(content)
    content = addKey(
        rowShift(halfByteSubstitude(addKey(columnMix(rowShift(halfByteSubstitude(addKey(content, k1)))), k2))), k3)
    return content


# 解密
def decode(key, content):
    k1, k2, k3 = generate_key(key)
    content = np.array(content)
    content = addKey(inverseHalfByteSubstitude(
        rowShift(inverseColumnMix(addKey(inverseHalfByteSubstitude(rowShift(addKey(content, k3))), k2)))), k1)
    return content


# 双重加密
def doubleEncode(key, content):
    firstKey = key[0:16]
    lastKey = key[16:32]
    return encode(lastKey, encode(firstKey, content))


# 双重解密
def doubleDecode(key, content):
    firstKey = key[0:16]
    lastKey = key[16:32]
    return decode(firstKey, decode(lastKey, content))


# 三重加密
def tripleEncode(key, content):
    firstKey = key[0:16]
    lastKey = key[16:32]
    return encode(firstKey, decode(lastKey, encode(firstKey, content)))


# 三重解密
def tripleDecode(key, content):
    firstKey = key[0:16]
    lastKey = key[16:32]
    return decode(firstKey, encode(lastKey, decode(firstKey, content)))


# 字符串转为二进制数组
def string_change(string):
    def int_to_16bit_bin_array(num):
        return np.array([int(b) for b in format(num, '016b')])

    def string_to_bin_arrays(s):
        return [int_to_16bit_bin_array(ord(c)) for c in s]

    arr = string_to_bin_arrays(string)
    arr = [np.array(list(c)) for c in arr]
    arr = [c.astype(int) for c in arr]
    return arr


# 加密字符串
def encode_str(key, string):
    arr = string_change(string)
    en_arr = [encode(key, c) for c in arr]
    en_arr = [c.astype(str) for c in en_arr]
    en_arr = [''.join(c.tolist()) for c in en_arr]
    en_arr = [int(c, 2) for c in en_arr]
    encoded_string = ''.join([chr(i) for i in en_arr])
    return encoded_string


# 解密字符串
def decode_str(key, string):
    arr = string_change(string)
    de_arr = [decode(key, c) for c in arr]
    de_arr = [c.astype(str) for c in de_arr]
    de_arr = [''.join(c.tolist()) for c in de_arr]
    de_arr = [int(c, 2) for c in de_arr]
    decoded_string = ''.join([chr(i) for i in de_arr])
    return decoded_string


# CBC加密字符串
def encodeCBCString(key, string):
    IV = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1])
    arr = string_change(string)
    en_arr = []
    for i in range(len(arr)):
        temp = np.bitwise_xor(arr[i], IV)
        IV = encode(key, temp)
        en_arr.append(IV)
    en_arr = [c.astype(str) for c in en_arr]
    en_arr = [''.join(c.tolist()) for c in en_arr]
    en_arr = [int(c, 2) for c in en_arr]
    encoded_string = ''.join([chr(i) for i in en_arr])
    return encoded_string


# CBC解密字符串
def decodeCBCString(key, string):
    firstIV = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1])
    arr = string_change(string)
    arr.reverse()
    de_arr = []
    for i in range(len(arr)):
        if i != len(arr) - 1:
            IV = arr[i + 1]
        else:
            IV = firstIV
        temp = decode(key, arr[i])
        temp = np.bitwise_xor(temp, IV)
        de_arr.append(temp)
    de_arr.reverse()
    de_arr = [c.astype(str) for c in de_arr]
    de_arr = [''.join(c.tolist()) for c in de_arr]
    de_arr = [int(c, 2) for c in de_arr]
    decoded_string = ''.join([chr(i) for i in de_arr])
    return decoded_string


# 相遇攻击破解双重加密
def brute_force_sdes(ciphertext, plaintext):
    possible_keys = []
    midTextA = {}
    midTextB = {}

    # 对每一个可能的keyA, 加密明文并存储中间结果
    for key in range(2 ** 16):
        binary_key = np.array([int(b) for b in format(key, '016b')])
        encoded_text = encode(binary_key, plaintext)
        midTextA[tuple(encoded_text)] = binary_key

    # 对每一个可能的keyB, 解密密文并存储中间结果
    for key in range(2 ** 16):
        binary_key = np.array([int(b) for b in format(key, '016b')])
        decoded_text = decode(binary_key, ciphertext)
        midTextB[tuple(decoded_text)] = binary_key

    # dataA = pd.DataFrame([midTextA.keys(), midTextA.values()], index=['mid', 'key1'])
    # dataA = dataA.transpose()
    # dataB = pd.DataFrame([midTextB.keys(), midTextB.values()], index=['mid', 'key2'])
    # dataB = dataB.transpose()
    # result = pd.merge(dataA, dataB, on='mid', how='inner')
    # 比较两个字典中的键，找到匹配项
    for encoded_text_str in midTextA.keys():
        if encoded_text_str in midTextB.keys():
            possible_keys.append(np.concatenate([midTextA.get(encoded_text_str), midTextB.get(encoded_text_str)]))

    return possible_keys


if __name__ == '__main__':
    pass
    # print(string_change('asdasdasd'))
    # k = brute_force_sdes([0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],
    #                      [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0]
    #                      )
    #
    # print(encode_str([1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0], 'HelloWorld'))
    # print(encodeCBCString([1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0], 'HelloWorld'))
    # print(doubleDecode([1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0],
    #                    [0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0]))
    # [0 1 0 0 1 1 1 0 0 0 1 0 1 0 0 0]
    # [1 0 0 0 1 0 1 0 0 0 0 1 1 1 0 0]
    # print(encode([0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0],
    #              encode([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                     [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0])))
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0]
    # [1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0]
    # 0    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    # 1    (0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0)
    # 2    (0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0)
    # 3    (1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0)
    # 4    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0)
    # Name: key1, dtype: object
    # 0    (0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0)
    # 1    (0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1)
    # 2    (1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0)
    # 3    (1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0)
    # 4    (0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0)
    # Name: key2, dtype: object

    # x = [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0]
    # print(rowShift(halfByteSubstitude(x)))
    # print(columnMix(rowShift(halfByteSubstitude(x))))
    # print(generate_key([0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]))
    # print(encode([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]))
    # print(decode([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], [1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0]))
