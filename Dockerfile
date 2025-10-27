# 使用基于 Debian 11 的 Python 镜像（支持 OpenSSL 1.x）
FROM python:3.12-slim-bullseye

# 设置工作目录
WORKDIR /app

# 配置 apt 镜像源并安装系统依赖（包括 ICU 库）
RUN rm -rf /etc/apt/sources.list.d/* \
    && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye main contrib non-free"            > /etc/apt/sources.list \
    && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian bullseye-updates main contrib non-free"    >> /etc/apt/sources.list \
    && echo "deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bullseye-security main contrib non-free" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libicu-dev \
        libicu67 \
        libgdiplus \
        libssl1.1 \
        openssl \
    && rm -rf /var/lib/apt/lists/*

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 配置 pip 镜像源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# 安装 uv 工具
RUN pip install uv

# 复制项目依赖文件
COPY pyproject.toml uv.lock* ./

# 安装项目依赖
RUN uv sync --frozen

# 设置 PATH
ENV PATH="/app/.venv/bin:$PATH"

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 7001

# 设置环境变量以支持全球化
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false
ENV ICU_DATA=/usr/share/icu

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7001"]