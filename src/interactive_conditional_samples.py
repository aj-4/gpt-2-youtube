#!/usr/bin/env python3

import fire
import json
import os
import re
import numpy as np
import tensorflow as tf

import model, sample, encoder

sampleComments = """
1: Great video, amazing.
2: Thanks glad you enjoyed it.

1: Would love to see you do a bot that messages people
2: Good idea I'll keep it in mind

1: Why did you change your hair?
2: It was getting too long.

1: Loving the beard bro
2: haha

1: So much value in this video
2: Cheers man

1: This was great, glad you are making this style of video
2: It's fun for me too, thanks.


1: Great, keep it up, proud of you.
2: Cheers bro

1: You're awesome bro.
2: You too.

1: Most honest YouTuber for sure.
2: I try to be.

1: Usually good but this one ain't it.
2: Thanks for the feedback

"""


def interact_model(
    model_name='774M',
    seed=None,
    nsamples=1,
    batch_size=1,
    length=100,
    temperature=1,
    top_k=0,
    top_p=1,
    models_dir='models',
    comments=[]
):
    """
    Interactively run the model
    :model_name=124M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to reproduce
     results
    :nsamples=1 : Number of samples to return total
    :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :temperature=1 : Float value controlling randomness in boltzmann
     distribution. Lower temperature results in less random completions. As the
     temperature approaches zero, the model will become deterministic and
     repetitive. Higher temperature results in more random completions.
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :models_dir : path to parent folder containing model subfolders
     (i.e. contains the <model_name> folder)
    """
    models_dir = os.path.expanduser(os.path.expandvars(models_dir))
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name, models_dir)
    hparams = model.default_hparams()
    with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(sess, ckpt)

        for comment in comments:
            raw_text = sampleComments + "1: " + comment['text'] + "\n"
            context_tokens = enc.encode(raw_text)
            generated = 0
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    generated += 1
                    text = enc.decode(out[i])
                    print("=" * 40 + " SAMPLE " + str(generated) + " " + "=" * 40)
                    try:
                        comment['res'] = (str(re.search("2\:.*", text).group(0))).split(':')[1]
                        print("in: ", comment['text'], "out: ", comment['res'])
                    except Exception as e:
                        print('failed to parse comment res')
            print("=" * 80)

        return comments

# if __name__ == '__main__':
#     fire.Fire(interact_model)

