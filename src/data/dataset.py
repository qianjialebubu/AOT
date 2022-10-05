import os
import math
import numpy as np
from glob import glob

from random import shuffle
from PIL import Image, ImageFilter

import torch
import torchvision.transforms.functional as F
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader

class InpaintingData(Dataset):
    def __init__(self, args):
        super(Dataset, self).__init__()
        self.w = self.h = args.image_size
        self.mask_type = args.mask_type
        
        # image and mask 
        self.image_path = []
        for ext in ['*.jpg', '*.png']:
            # print((os.path.join(args.dir_image, args.data_train, ext)))/data3/qianjiale_dataset/project/AOT/src/data/dataset.py
            # self.image_path.extend(glob(os.path.join(args.dir_image, args.data_train, ext)))
            self.image_path.extend(glob(r"/data3/qianjiale_dataset/celeba_mask_256/*.jpg"))
            # self.image_path=("D:\file\program_data\deeplearning\AOT-GAN-for-Inpainting-master\src\dir_image/celeba-64/*.jpg")
            # mm = "dir_image\\celeba-64\\*.jpg"
            # self.image_path =mm
            # print("Image path: {}".format(self.image_path))
        # self.mask_path = glob(os.path.join(args.dir_mask, args.mask_type, '*.png'))
        self.mask_path = []
        for ext in ['*.jpg', '*.png']:
            self.mask_path.extend(glob(r"/data3/qianjiale_dataset/celeba_mask_256/*.jpg"))
            # print("mask path: {}".format(self.mask_path))

        # augmentation
        # 进行图像的预处理
        self.img_trans = transforms.Compose([
            transforms.RandomResizedCrop(args.image_size),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.05, 0.05, 0.05, 0.05),
            transforms.ToTensor()])
        self.mask_trans = transforms.Compose([
            transforms.Resize(args.image_size, interpolation=transforms.InterpolationMode.NEAREST),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(
                (0, 45), interpolation=transforms.InterpolationMode.NEAREST),
        ])

        
    def __len__(self):
        # print(len(self.image_path))
        return len(self.image_path)

    def __getitem__(self, index):
        # load image
        image = Image.open(self.image_path[index]).convert('RGB')
        filename = os.path.basename(self.image_path[index])
        if self.mask_type == 'pconv':
            index = np.random.randint(0, len(self.mask_path))
            mask = Image.open(self.mask_path[index])
            mask = mask.convert('L')

        else:
            mask = np.zeros((self.h, self.w)).astype(np.uint8)
            mask[self.h//4:self.h//4*3, self.w//4:self.w//4*3] = 1
            mask = Image.fromarray(mask).convert('L')
        
        # augment
        image = self.img_trans(image) * 2. - 1.
        mask = F.to_tensor(self.mask_trans(mask))

        return image, mask, filename



if __name__ == '__main__': 

    from attrdict import AttrDict

    args = {
        'dir_image': '/data3/qianjiale_dataset',
        'data_train': 'celeba-256',
        'dir_mask': '/data3/qianjiale_dataset',
        'mask_type': 'pconv',
        'image_size': 256
    }
    args = AttrDict(args)


    data = InpaintingData(args)
    # print(len(data), len(data.mask_path))
    img, mask, filename = data[0]
    # print(img.size(), mask.size(), filename)