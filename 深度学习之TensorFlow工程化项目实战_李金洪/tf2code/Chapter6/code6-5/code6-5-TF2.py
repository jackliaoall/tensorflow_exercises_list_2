# -*- coding: utf-8 -*-
"""
@author: 代码医生工作室
@公众号：xiangyuejiqiren   （内有更多优秀文章及学习资料）
@来源: <深度学习之TensorFlow工程化项目实战>配套代码 （700+页）
@配套代码技术支持：bbs.aianaconda.com      (有问必答)
"""

#使用动态图训练一个具有检查点的回归模型

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
tf.compat.v1.disable_v2_behavior()

#（1）生成模拟数据
train_X = np.linspace(-1, 1, 100)
train_Y = 2 * train_X + np.random.randn(*train_X.shape) * 0.3 # y=2x，但是加入了噪声
#图形显示
plt.plot(train_X, train_Y, 'ro', label='Original data')
plt.legend()
plt.show()

tf.compat.v1.reset_default_graph()

def my_py_func(X, W,b):
  z = tf.multiply(X, W)+ b
  print(z)
  return z


#（2）建立网络模型

# 创建模型
# 占位符
X = tf.compat.v1.placeholder("float")
Y = tf.compat.v1.placeholder("float")
# 模型参数
W = tf.Variable(tf.random.normal([1]), name="weight")
b = tf.Variable(tf.zeros([1]), name="bias")
# 前向结构
#z = tf.multiply(X, W)+ b


z = tf.py_function(my_py_func, [X, W,b], tf.float32)
global_step = tf.Variable(0, name='global_step', trainable=False)
#反向优化
cost =tf.reduce_mean( input_tensor=tf.square(Y - z))
learning_rate = 0.01
optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate).minimize(cost,global_step) #梯度下降

# 定义学习参数
training_epochs = 34
display_step = 2

savedir = "log/"
saver = tf.compat.v1.train.Saver(tf.compat.v1.global_variables(), max_to_keep=1)#生成saver。 max_to_keep=1，表明最多只保存一个检查点文件

#定义生成loss可视化的函数
plotdata = { "batchsize":[], "loss":[] }
def moving_average(a, w=10):
    if len(a) < w:
        return a[:]
    return [val if idx < w else sum(a[(idx-w):idx])/w for idx, val in enumerate(a)]

#（3）建立session进行训练
with tf.compat.v1.Session() as sess:
    sess.run(tf.compat.v1.global_variables_initializer())
    kpt = tf.train.latest_checkpoint(savedir)
    if kpt!=None:
        saver.restore(sess, kpt)

    # 向模型输入数据
    while global_step.eval()/len(train_X) < training_epochs:
        step = int( global_step.eval()/len(train_X) )
        for (x, y) in zip(train_X, train_Y):
            sess.run(optimizer, feed_dict={X: x, Y: y})

        #显示训练中的详细信息
        if step % display_step == 0:
            loss = sess.run(cost, feed_dict={X: train_X, Y:train_Y})
            print ("Epoch:", step+1, "cost=", loss,"W=", sess.run(W), "b=", sess.run(b))
            if not (loss == "NA" ):
                plotdata["batchsize"].append(global_step.eval())
                plotdata["loss"].append(loss)
            saver.save(sess, savedir+"linermodel.cpkt", global_step)

    print (" Finished!")
    saver.save(sess, savedir+"linermodel.cpkt", global_step)

    print ("cost=", sess.run(cost, feed_dict={X: train_X, Y: train_Y}), "W=", sess.run(W), "b=", sess.run(b))

    #显示模型

    plt.plot(train_X, train_Y, 'ro', label='Original data')
    v = sess.run(z, feed_dict={X: train_X})
    plt.plot(train_X, v, label='Fitted line')
    plt.legend()
    plt.show()

    plotdata["avgloss"] = moving_average(plotdata["loss"])
    plt.figure(1)
    plt.subplot(211)
    plt.plot(plotdata["batchsize"], plotdata["avgloss"], 'b--')
    plt.xlabel('Minibatch number')
    plt.ylabel('Loss')
    plt.title('Minibatch run vs. Training loss')

    plt.show()
