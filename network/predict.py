import os
import json

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

model_weight_path = "./network/weights/xbest_model_g.pth"
if 'xx' in model_weight_path:
    from network.model import mobile_vit_xx_small as create_model
else:
    from network.model import mobile_vit_x_small as create_model
class_indict = {
    "0": "ng",
    "1": "ok"
}


class Predict:
    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        img_size = 224
        self.data_transform = transforms.Compose(
            [transforms.Resize(int(img_size * 1.14)),
             transforms.CenterCrop(img_size),
             transforms.ToTensor(),
             transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        # read class_indict
        # json_path = './network/class_indices.json'
        # assert os.path.exists(json_path), "file: '{}' dose not exist.".format(json_path)
        #
        # with open(json_path, "r") as f:
        #     class_indict = json.load(f)

        # create model
        self.model = create_model(num_classes=2).to(self.device)
        # load model weights
        self.model.load_state_dict(torch.load(model_weight_path, map_location=self.device))
        self.model.eval()

    def to_predict(self, imgdata: np.ndarray):
        # assert os.path.exists(img_path), "file: '{}' dose not exist.".format(img_path)
        # img = Image.open(img_path)
        img = Image.fromarray(imgdata)
        # [N, C, H, W]
        img = self.data_transform(img)
        # expand batch dimension
        img = torch.unsqueeze(img, dim=0)
        with torch.no_grad():
            # predict class
            output = torch.squeeze(self.model(img.to(self.device))).cpu()
            predict = torch.softmax(output, dim=0)
            predict_cla = torch.argmax(predict).numpy()
        # print_res = "class: {}   prob: {:.3}".format(class_indict[str(predict_cla)],
        #                                              predict[predict_cla].numpy())
        return predict_cla, class_indict[str(predict_cla)], predict[predict_cla].numpy()
