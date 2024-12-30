from django.shortcuts import render
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
from .models import Topic
import warnings
import pandas as pd
import joblib

# 加载模型和Scaler
model = joblib.load('../../back/model/xgb_model.pkl')
scaler = joblib.load('../../back/model/scaler.pkl')

# Create your views here.
def index(request):
    """学习笔记的主页"""
    return render(request, 'learning_logs/index.html')

def topics(request):
    """显示所有主题"""
    topics = Topic.objects.order_by('date_added')
    context = {'topics':topics}
    return render(request, 'learning_logs/topics.html', context)


def predict(request):
    if request.method == 'POST':
        # 获取并转换输入值，确保它们是整数类型
        user_input_year = int(request.POST.get('user_input_year', '0'))
        user_input_fans = int(request.POST.get('user_input_fans', '0'))
        user_input_views = int(request.POST.get('user_input_views', '0'))
        user_input_likes = int(request.POST.get('user_input_likes', '0'))
        user_input_coins = int(request.POST.get('user_input_coins', '0'))
        user_input_collects = int(request.POST.get('user_input_collects', '0'))
        user_input_part = request.POST.get('user_input_part', '')  # part 字段保留为字符串

        # 在这里进行你需要的处理
        is_high_quality = process_final(user_input_year, user_input_fans, user_input_views,
                                        user_input_likes, user_input_coins, user_input_collects, user_input_part)

        return render(request, 'learning_logs/predict.html', {'year': user_input_year,
        'fans': user_input_fans, 'likes': user_input_likes,
        'views': user_input_views, 'coins': user_input_coins,
        'collects': user_input_collects, 'is_high_quality':is_high_quality})


    return render(request, 'learning_logs/input.html')

def process_final(year, fans, views, likes, coins, collects, part):
# 预处理函数
    def preprocess_new_user(new_user_df, scaler, training_features):
        # a. 处理缺失值（如果有）
        new_user_df = new_user_df.ffill()

        # b. 编码分类变量 'part' 使用独热编码
        new_user_df = pd.get_dummies(new_user_df, columns=['part'], drop_first=True)

        # c. 移除不必要的列 'username'
        new_user_df = new_user_df.drop(['username'], axis=1)

        # d. 创建衍生特征
        new_user_df['likes_per_fan'] = new_user_df['likes'] / (new_user_df['fans'] + 1)
        new_user_df['coins_per_fan'] = new_user_df['coins'] / (new_user_df['fans'] + 1)
        new_user_df['collect_per_fan'] = new_user_df['collects'] / (new_user_df['fans'] + 1)
        new_user_df['total_interactions'] = new_user_df['likes'] + new_user_df['coins'] + new_user_df['collects']

        # 计算 'num_parts'（发布的视频分区数量）
        part_columns = [col for col in new_user_df.columns if 'part_' in col]
        if part_columns:
            new_user_df['num_parts'] = new_user_df[part_columns].sum(axis=1)
        else:
            new_user_df['num_parts'] = 1  # 如果没有独热编码的part，假设为1

        # e. 标准化数值特征
        numerical_features = ['fans', 'likes', 'views', 'coins', 'collects', 'year',
                              'likes_per_fan', 'coins_per_fan', 'collect_per_fan',
                              'total_interactions', 'num_parts']

        # 如果某些衍生特征在新数据中缺失，需要添加并填充
        for feature in numerical_features:
            if feature not in new_user_df.columns:
                new_user_df[feature] = 0  # 或其他适当的填充值

        # 标准化
        new_user_df[numerical_features] = scaler.transform(new_user_df[numerical_features])

        # f. 确保特征与训练时一致
        # 添加缺失的独热编码列（与训练时的特征保持一致）
        for feature in training_features:
            if feature not in new_user_df.columns:
                new_user_df[feature] = 0

        # 确保列的顺序与训练时相同
        new_user_df = new_user_df[training_features]

        return new_user_df

    # 主函数
    def main():
        # 新用户数据示例
        new_user = {'username':'lbl', 'year': year, 'fans': fans, 'views': views, 'likes': likes, 'coins': coins, 'collects': collects, 'part': part}

        # 转换为 DataFrame
        new_user_df = pd.DataFrame([new_user])

        # 获取训练时的特征名称
        training_features = model.get_booster().feature_names

        # 预处理新用户数据
        processed_new_user = preprocess_new_user(new_user_df, scaler, training_features)

        # 进行预测
        prediction = model.predict(processed_new_user)
        prediction_proba = model.predict_proba(processed_new_user)[:, 1]

        # 输出预测结果
        is_top100 = prediction[0]
        probability = prediction_proba[0]

        if is_top100 == 1:
            return 1
        else:
            return 0

    is_high_quality = main()
    return is_high_quality