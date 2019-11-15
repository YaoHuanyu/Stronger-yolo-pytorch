import torch.nn as nn
from collections import OrderedDict
class conv_bn(nn.Module):
    def __init__(self,inp, oup, kernel,stride,padding):
        super(conv_bn, self).__init__()
        self.convbn=nn.Sequential(OrderedDict([
            ('conv', nn.Conv2d(inp, oup, kernel, stride, padding, bias=False)),
            ('bn', nn.BatchNorm2d(oup)),
            ('relu', nn.ReLU6(inplace=True))
        ]))
    def forward(self, input):
        return self.convbn(input)

class conv_bias(nn.Module):
    def __init__(self,inp, oup, kernel,stride,padding):
        super(conv_bias, self).__init__()
        self.conv=nn.Conv2d(inp, oup, kernel, stride, padding, bias=True)
    def forward(self, input):
        return self.conv(input)

class sepconv_bn(nn.Module):
    def __init__(self,inp, oup, kernel,stride,padding):
        super(sepconv_bn, self).__init__()
        self.sepconv_bn= nn.Sequential(OrderedDict([
            ('sepconv',nn.Conv2d(inp, inp, kernel, stride, padding,groups=inp, bias=False)),
            ('sepbn',nn.BatchNorm2d(inp)),
            ('seprelu',nn.ReLU6(inplace=True)),
            ('pointconv', nn.Conv2d(inp, oup, 1, 1, 0, bias=False)),
            ('pointbn', nn.BatchNorm2d(oup)),
            ('pointrelu', nn.ReLU6(inplace=True)),
        ]))
    def forward(self, input):
        return self.sepconv_bn(input)

class InvertedResidual(nn.Module):
    def __init__(self, inp, oup, stride, expand_ratio):
        super(InvertedResidual, self).__init__()
        self.stride = stride
        assert stride in [1, 2]
        hidden_dim = round(inp * expand_ratio)
        self.use_res_connect = self.stride == 1 and inp == oup
        if expand_ratio == 1:
            self.conv=nn.Sequential(OrderedDict([
                ('dw_conv', nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False)),
                ('dw_bn', nn.BatchNorm2d(hidden_dim)),
                ('dw_relu', nn.ReLU6(inplace=True)),
                ('project_conv', nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False)),
                ('project_bn', nn.BatchNorm2d(oup))
            ]))
        else:
            self.conv = nn.Sequential(OrderedDict(
                [
                    ('expand_conv',nn.Conv2d(inp, hidden_dim, 1, 1, 0, bias=False)),
                    ('expand_bn', nn.BatchNorm2d(hidden_dim)),
                    ('expand_relu', nn.ReLU6(inplace=True)),
                    ('dw_conv',nn.Conv2d(hidden_dim, hidden_dim, 3, stride, 1, groups=hidden_dim, bias=False)),
                    ('dw_bn',nn.BatchNorm2d(hidden_dim)),
                    ('dw_relu',nn.ReLU6(inplace=True)),
                    ('project_conv',nn.Conv2d(hidden_dim, oup, 1, 1, 0, bias=False)),
                    ('project_bn',nn.BatchNorm2d(oup))
                ]
            )
            )

    def forward(self, x):
        if self.use_res_connect:
            return x + self.conv(x)
        else:
            return self.conv(x)

class DarknetBlock(nn.Module):
  def __init__(self, inplanes, planes):
    super(DarknetBlock, self).__init__()
    self.conv1 = nn.Conv2d(inplanes, planes[0], kernel_size=1,
                           stride=1, padding=0, bias=False)
    self.bn1 = nn.BatchNorm2d(planes[0])
    self.relu1 = nn.LeakyReLU(0.1)
    self.conv2 = nn.Conv2d(planes[0], planes[1], kernel_size=3,
                           stride=1, padding=1, bias=False)
    self.bn2 = nn.BatchNorm2d(planes[1])
    self.relu2 = nn.LeakyReLU(0.1)

  def forward(self, x):
    residual = x

    out = self.conv1(x)
    out = self.bn1(out)
    out = self.relu1(out)

    out = self.conv2(out)
    out = self.bn2(out)
    out = self.relu2(out)

    out += residual
    return out