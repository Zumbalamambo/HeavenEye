import cv2
import numpy as np
import tensorflow as tf
import os
import json
import threading

import FaceDetection


def to_rgb(img):
    w, h = img.shape
    ret = np.empty((w, h, 3), dtype=np.uint8)
    ret[:, :, 0] = ret[:, :, 1] = ret[:, :, 2] = img
    return ret


# face detection parameters
minsize = 20  # minimum size of face
threshold = [0.6, 0.7, 0.7]  # three steps's threshold
factor = 0.709  # scale factor

# restore mtcnn model
print('Creating networks and loading parameters')
gpu_memory_fraction = 1.0
with tf.Graph().as_default():
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
    config = tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False)
    config.gpu_options.allow_growth = True
    sess = tf.Session(config=config)
    with sess.as_default():
        pnet, rnet, onet = FaceDetection.create_mtcnn(sess, './model_check_point/')

path = "/share/dataset/val/1_2_04_1/prob/dongnanmeneast_15_1920x1080_30/"
save_path = "/mnt/disk/faces_test_west/"
# path = "."
# save_path = "./test/"
all_face_positions = {}


def detect_face_with_range(start_index, end_index):
    for now_index in xrange(start_index, end_index + 1):
        file_name = str(now_index) + ".jpg"
        if not os.path.exists(os.path.join(path, file_name)):
            continue

        pic = cv2.imread(os.path.join(path, file_name))

        find_results = []
        gray = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)

        img = to_rgb(gray)
        width, height = gray.shape

        bounding_boxes, _ = FaceDetection.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
        print("Detect {} face in {}".format(len(bounding_boxes), file_name))

        number_of_faces = bounding_boxes.shape[0]  # number of faces

        index = 0
        img_dir = os.path.join(save_path, file_name)
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        face_positions = []
        for face_position in bounding_boxes:
            face_position = face_position.astype(int)
            face_position[1] = 0 if face_position[1] < 0 else face_position[1]
            face_position[3] = width - 1 if face_position[3] > width else face_position[3]
            face_position[0] = 0 if face_position[0] < 0 else face_position[0]
            face_position[2] = height - 1 if face_position[2] > height else face_position[2]

            cv2.rectangle(pic,
                          (face_position[0],
                           face_position[1]),
                          (face_position[2],
                           face_position[3]),
                          (0, 255, 0), 2)

            crop = img[face_position[1]:face_position[3], face_position[0]:face_position[2], ]
            crop = cv2.resize(crop, (96, 96), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(os.path.join(img_dir, str(index) + ".png"), crop)
            face_positions.append((0.8,
                                   face_position[0],
                                   face_position[1],
                                   face_position[2],
                                   face_position[3]))
            index += 1

        all_face_positions[file_name] = face_positions


th1 = threading.Thread(target=detect_face_with_range, args=(18082, 18500))
th1.start()
th2 = threading.Thread(target=detect_face_with_range, args=(18501, 18900))
th2.start()
th3 = threading.Thread(target=detect_face_with_range, args=(18901, 19300))
th3.start()
th4 = threading.Thread(target=detect_face_with_range, args=(19301, 19700))
th4.start()
th5 = threading.Thread(target=detect_face_with_range, args=(19701, 20100))
th5.start()
th6 = threading.Thread(target=detect_face_with_range, args=(20101, 20400))
th6.start()
th7 = threading.Thread(target=detect_face_with_range, args=(20401, 20688))
th7.start()
th1.join()
th2.join()
th3.join()
th4.join()
th5.join()
th6.join()
th7.join()

with open(os.path.join(save_path, "position.json"), 'w') as outfile:
    json.dump(all_face_positions, outfile)

# Display the resulting frame
# cv2.imshow('face_detection', pic)
# while True:
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything is done, release the capture
# cv2.destroyAllWindows()
