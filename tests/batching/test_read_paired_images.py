"""
Read and show paired images from a tfrecord

Run from the top folder as:
python3 -m dataset.batching.test_read_paired_images
"""
import unittest
from os.path import basename

import matplotlib.pyplot as plt
import tensorflow as tf

from dataset.shared import dir_tfrecord
from dataset.tfrecords import ImagePairRecordReader


class TestPairedImagesRead(unittest.TestCase):
    def test_paired_images_read(self):
        # Important: read_batch MUST be called before start_queue_runners,
        # otherwise the internal shuffle queue gets created but its
        # threads won't start
        irr = ImagePairRecordReader('images_0.tfrecord', dir_tfrecord)
        read_one_example = irr.read_one()
        read_batched_examples = irr.read_batch(10)

        with tf.Session() as sess:
            sess.run([tf.global_variables_initializer(),
                      tf.local_variables_initializer()])

            # Coordinate the loading of image files.
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(coord=coord)

            # Reading images sequentially one by one
            # Note: Images in the range [-1, 1] need to be converted
            #       to [0, 1] for matplotlib to show them  correctly
            for i in range(0, 8, 2):
                res = sess.run(read_one_example)
                plt.subplot(2, 4, i + 1)
                plt.imshow((res['input_image'] + 1) / 2)
                plt.title('Input (filtered)')
                plt.axis('off')
                plt.subplot(2, 4, i + 2)
                plt.imshow((res['target_image'] + 1) / 2)
                plt.title('Target (unfiltered)')
                plt.axis('off')
                print('Read:',
                      '\n\tinput', basename(res['input_file']),
                      '\n\ttarget', basename(res['target_file']),
                      '\n\tembedding', res['input_embedding'])
            plt.show()

            # Reading images in batch
            res = sess.run(read_batched_examples)
            print(res['input_image'].shape,
                  res['target_image'].shape,
                  res['input_embedding'].shape)

            # Finish off the filename queue coordinator.
            coord.request_stop()
            coord.join(threads)


if __name__ == '__main__':
    unittest.main()
