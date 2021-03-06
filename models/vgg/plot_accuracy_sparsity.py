#!/usr/bin/env python

import sys
import re

# plotting
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.backends.backend_pdf import PdfPages

net_re = re.compile('^net:.*/train_val_(.*)\.prototxt')
model_re1 = re.compile('Finetuning from models/resnet/[^/]*/(.*)\.caffemodel')
model_re2 = re.compile('Finetuning from models/resnet/(.*)\.caffemodel')
model_re3 = re.compile('Resuming from models/resnet/([^/]*)/.*\.solverstate')
weight_decay_re = re.compile('weight_decay: (.+)')

layer_names = [
'conv1_1', # 1
'conv1_2', # 2
'conv2_1', # 3
'conv2_2', # 4
'conv3_1', # 5
'conv3_2', # 6
'conv3_3', # 7
'conv4_1', # 8
'conv4_2', # 9
'conv4_3', # 10
'conv5_1', # 11
'conv5_2', # 12
'conv5_3', # 13
'fc6',     # 14
'fc7',     # 15
'fc8',     # 16
]

accuracy_re = re.compile('Test net output \#\d+: accuracy@1 = (\d+\.\d+)')
accuracy_top5_re = re.compile('Test net output \#\d+: accuracy@5 = (\d+\.\d+)')
#accuracy_re = re.compile('Test net output \#\d+: accuracy = (\d+\.\d+)')
iteration_re = re.compile('Iteration (\d+), loss')

sparsity_re_string = '^'
for i in range(len(layer_names)):
  sparsity_re_string += '(\d+\.?\d*)\W+'

sparsity_re = re.compile(sparsity_re_string)
#sparsity_re = re.compile('^(\d+\.?\d*)\W+(\d+\.?\d*)\W+(\d+\.?\d*)\W+(\d+\.?\d*)\W+(\d+\.?\d*)\W+(\d+\.?\d*)\W+(\d+\.?\d*)\W+(\d+\.?\d*)')

#plt.xlabel('Iteration')
#plt.ylabel('Accuracy (validation) / Sparsity')

net = None
model = None
weight_decay = None

accuracy = []
accuracy_top5 = []
iteration = []
sparsity = []
for i in range(len(layer_names)):
  sparsity.append([])

model = sys.argv[1]
files = [model]
while model:
  with open(model + "/train.info") as logfile:
    model = None
    for line in logfile:
      m = model_re3.search(line)
      if m:
        model = m.group(1)
        files.insert(0, model)

for f in files:
  print f + "->",
print

for f in files:
  mode = 0 # 0 : looking for accuracy, 1: looking for iteration, 2: looking for sparsity
  with open(f + "/train.info") as logfile:
    for line in logfile:
      m = net_re.search(line)
      if m:
        net = m.group(1)

      m = model_re1.search(line)
      if m:
        model = m.group(1)
      else:
        m = model_re2.search(line)
        if m:
          model = m.group(1)
        else:
          m = model_re3.search(line)
          if m:
            model = m.group(1)

      m = weight_decay_re.search(line)
      if m:
        weight_decay = m.group(1)

      if mode == 0:
        m = accuracy_re.search(line)
        if m:
          accuracy.append(float(m.group(1)))
          mode = 1
      elif mode == 1:
        m = accuracy_top5_re.search(line)
        if m:
          accuracy_top5.append(float(m.group(1)))
          mode = 2
      elif mode == 2:
        m = iteration_re.search(line)
        if m:
          iteration.append(int(m.group(1)))
          mode = 3
      elif mode == 3:
        m = sparsity_re.search(line)
        if m:
          for i in range(len(layer_names)):
            sparsity[i].append(float(m.group(i + 1))/100)
          mode = 0

#print len(iteration)
#print len(accuracy)
#for i in range(8):
  #print len(sparsity[i])

#for i in range(len(accuracy)):
  #print iteration[i], accuracy[i],
  #for j in range(8):
    #print sparsity[j][i],
  #print
min_len = min(len(iteration), len(accuracy))

fig, ax1 = plt.subplots()
ax1.plot(iteration[:min_len], accuracy[:min_len], label='top1', marker='*')
ax1.plot(iteration[:min_len], accuracy_top5[:min_len], label='top5', marker='*')
ax1.set_ylabel('accuracy (validation)')
ax1.set_xlabel('iteration')

ax2 = ax1.twinx()
viridis = plt.get_cmap('jet')
cNorm = colors.Normalize(vmin=0, vmax=len(layer_names))
scalarMap = cmx.ScalarMappable(norm = cNorm, cmap=viridis)
for i in range(len(layer_names)):
  ax2.plot(iteration, sparsity[i][:min_len], label=layer_names[i], color=scalarMap.to_rgba(i))
#for i in range(5,8):
  #ax2.plot(iteration, sparsity[i][:min_len], label=('l' + str(i + 1)), marker='+')
#ax2.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=9,mode="expand", borderaxespad=0.)
ax2.set_ylabel('sparsity')
#plt.legend(bbox_to_anchor=(0.9, 1), loc=2, borderaxespad=0.)
#ax = plt.subplot(111)
#box = ax.get_position()
#ax.set_position([box.x0, box.y0, box.width, box.height*0.7])
#ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.6))

#if len(sys.argv) > 1
  #outfile = sys.argv[-1]
#else
#outfile = net + "_" + model + "_" + weight_decay + ".png"
outfile = sys.argv[1] + ".png"
plt.savefig(outfile)
