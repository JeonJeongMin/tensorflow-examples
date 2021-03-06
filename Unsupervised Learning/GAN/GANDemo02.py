import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('./Data/mnist.data/',one_hot = True)

total_epoch = 100
batch_size = 100
n_hidden = 256
n_input = 28*28
n_noise = 128
n_class = 10

X = tf.placeholder(tf.float32, [None, n_input])
Y = tf.placeholder(tf.float32, [None, n_class])
Z = tf.placeholder(tf.float32, [None, n_noise])

global_step = tf.Variable(0,trainable=True, name='global_step')

def generator(noise,labels):
    with tf.variable_scope('generator'):
        inputs = tf.concat([noise, labels], 1)
        hidden = tf.layers.dense(inputs, n_hidden,
                                 activation =tf.nn.relu)
        output = tf.layers.dense(hidden,n_input,
                                 activation=tf.nn.sigmoid)
    return output
        
def discriminator(inputs, labels, reuse=None):
    with tf.variable_scope('discriminator') as scope:
        if reuse:
            scope.reuse_variables()

        inputs = tf.concat([inputs, labels],1)
        hidden = tf.layers.dense(inputs, n_hidden, activation=tf.nn.relu)
        output = tf.layers.dense(hidden, 1, activation=None)

    return output

def get_noise(batch_size, n_noise):
    return np.random.uniform(-1.,1.,size=[batch_size, n_noise])

G = generator(Z,Y)
D_real = discriminator(X,Y)
D_gene = discriminator(G,Y,True)

loss_D_real = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
    logits=D_real, labels=tf.ones_like(D_real)))
loss_D_gene = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
    logits=D_gene, labels=tf.zeros_like(D_gene)))

loss_D = loss_D_real + loss_D_gene

loss_G = tf.reduce_mean(
    tf.nn.sigmoid_cross_entropy_with_logits(logits=D_gene,labels=tf.ones_like(D_gene)))

vars_D = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                           scope='discriminator')
vars_G = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES,
                           scope='generator')

train_D = tf.train.AdamOptimizer().minimize(loss_D,var_list = vars_D, global_step = global_step)
train_G = tf.train.AdamOptimizer().minimize(loss_G,var_list = vars_G, global_step = global_step)


sess = tf.Session()
#sess.run(tf.global_variables_initializer())

total_batch = int(mnist.train.num_examples/batch_size)
loss_val_D, loss_val_G = 0, 0

#
saver = tf.train.Saver(tf.global_variables())
ckpt = tf.train.get_checkpoint_state('./Saver/GanDemo02')
if ckpt and tf.train.checkpoint_exists(ckpt.model_checkpoint_path):
    saver.restore(sess, ckpt.model_checkpoint_path)
else:
    sess.run(tf.global_variables_initializer())
#
for epoch in range(0):
    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        noise = get_noise(batch_size, n_noise)

        _,loss_val_D = sess.run([train_D, loss_D],
                                feed_dict = {X:batch_xs, Y:batch_ys, Z:noise})
        _,loss_val_G = sess.run([train_G, loss_G],
                                feed_dict = {Y:batch_ys, Z:noise})
    snap = (int)(sess.run(global_step)/(2*total_batch)-1.0)#saver를 사용하기 위해 
    print('Epoch:', '%04d'%snap,
          'D loss: {:.4}'.format(loss_val_D),
          'G loss: {:.4}'.format(loss_val_G))

    
    if snap == 0 or (snap+1)%10==0:
        sample_size = 10
        noise = get_noise(sample_size, n_noise)
        samples = sess.run(G,
                           feed_dict={Y:mnist.test.labels[:sample_size],Z:noise})
        fig, ax = plt.subplots(2, sample_size, figsize=(sample_size, 2))
        for i in range(sample_size):
            ax[0][i].set_axis_off()
            ax[1][i].set_axis_off()

            ax[0][i].imshow(np.reshape(mnist.test.images[i],(28,28)))
            ax[1][i].imshow(np.reshape(samples[i], (28,28)))

        plt.savefig('./Sample/GANDemo02/{}.png'.format(str(snap).zfill(3)),
                    bbox_inches='tight')
        plt.close(fig)

saver.save(sess, './Saver/GanDemo02/GanDemo02.ckpt',global_step = global_step)


print('Learning Finished!')

def one_hot(i):
	return sess.run(tf.one_hot([i],10))

def sample_show(i):
    a=sess.run(tf.one_hot([i],10))
    for k in range(9):
        a=np.append(a,one_hot(i),axis=0)
        
    sample = sess.run(G,feed_dict={Y:a,Z:get_noise(10,128)})
    fig, ax = plt.subplots(1, 10, figsize=(10, 1))
    for k in range(10):
            ax[k].set_axis_off()
            ax[k].imshow(np.reshape(sample[k],(28,28)))
    
    plt.show()
