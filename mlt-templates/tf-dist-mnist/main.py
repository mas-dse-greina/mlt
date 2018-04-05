#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#


import json
import logging
import numpy as np
import os
import socket
import subprocess
import tensorflow as tf
import time

# You can turn on the gRPC messages by setting the environment variables below
# os.environ["GRPC_VERBOSITY"]="DEBUG"
# os.environ["GRPC_TRACE"] = "all"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Get rid of the AVX, SSE

# Define parameters
FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_float("learning_rate", 0.2, "Initial learning rate.")
tf.app.flags.DEFINE_integer("steps_to_validate", 10,
                            "Validate and print loss after this many steps")
tf.app.flags.DEFINE_integer("is_sync", 1, "Synchronous updates?")
tf.app.flags.DEFINE_string("train_dir", "/output", "directory to write "
                                                   "checkpoint files")
tf.app.flags.DEFINE_integer("num_epochs", 5, "number of epochs")
tf.app.flags.DEFINE_integer("batch_size", 1024, "batch size")
# Number of threads should be a few less than cpu cores.
tf.app.flags.DEFINE_integer("intraop_threads", max(os.cpu_count()-2, 1),
                            "Number of intraop parallel threads")
tf.app.flags.DEFINE_integer("interop_threads", 2,
                            "Number of interop parallel threads")


def main(_):
    start_time = time.time()

    logging.info("TensorFlow version: %s", tf.__version__)
    logging.info("TensorFlow git version: %s", tf.__git_version__)

    tf_config_json = os.environ.get("TF_CONFIG", "{}")
    tf_config = json.loads(tf_config_json)
    logging.info("tf_config: %s", tf_config)

    task = tf_config.get("task", {})
    task_index = task["index"]
    job_name = task["type"]
    logging.info("task: %s", task)

    cluster_spec = tf_config.get("cluster", {})
    logging.info("cluster_spec: %s", cluster_spec)
    worker_list = cluster_spec.get("worker", "{}")
    ps_list = cluster_spec.get("ps", "{}")

    logging.info("job_name: {}".format(job_name))
    logging.info("task_index: {}".format(task_index))

    config = tf.ConfigProto(
        inter_op_parallelism_threads=FLAGS.intraop_threads,
        intra_op_parallelism_threads=FLAGS.interop_threads)

    run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
    run_metadata = tf.RunMetadata()  # For Tensorflow trace

    cluster = tf.train.ClusterSpec(cluster_spec)
    server = tf.train.Server(cluster, job_name=job_name, task_index=task_index)

    if job_name == "ps":

        logging.info("\n")
        logging.info("*" * 30)
        logging.info("\nParameter server #{} on this machine.\n\nWaiting on "
                     "workers to finish.\n\nPress CTRL-\\ to terminate early."
                     .format(task_index))
        logging.info("*" * 30)

        server.join()

    elif job_name == "worker":

        is_chief = (task_index == 0)  # Am I the chief node?

        if is_chief:
            logging.info("I am chief worker {} with task #{}".format(
                worker_list[task_index], task_index))
        else:
            logging.info("I am worker {} with task #{}".format(
                worker_list[task_index], task_index))

        """
        BEGIN: Define model
        """
        a = tf.Variable(tf.truncated_normal(shape=[2]), dtype=tf.float32)
        b = tf.Variable(tf.truncated_normal(shape=[2]), dtype=tf.float32)
        c = a + b

        target = tf.constant(100., shape=[2], dtype=tf.float32)
        loss = tf.reduce_mean(tf.square(c - target))

        opt = tf.train.GradientDescentOptimizer(.0001).minimize(loss)
        """
        END: Define model
        """

        # Monitored Training Session for Distributed TensorFlow
        sess = tf.train.MonitoredTrainingSession(
            master=server.target,
            config=config,
            # checkpoint_dir="gs://constant-cubist-173123_cloudbuild/temp/",
            is_chief=is_chief)

        # The job should take more than a few minutes to run.
        # If you have a job that takes < 2 minutes to run then
        # it is possible for the chief worker to finish before the
        # other workers have started and then the other workers
        # are stalled forever.
        for i in range(100000):
            if sess.should_stop():
                break
            sess.run(opt)
            if i % 10 == 0:
                r = sess.run(c)
                logging.info("{}: {}".format(i, r))

        logging.info("Finished work on this node.")
        logging.info("Kubernetes should close parameter servers.")
        logging.info("Finished in {} seconds".format(time.time() - start_time))
        sess.close()


if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)
    tf.app.run()
