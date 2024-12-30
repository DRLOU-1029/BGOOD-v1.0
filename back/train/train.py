import pandas as pd

# 数据预处理与特征工程
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import xgboost as xgb

# 可视化
import matplotlib.pyplot as plt

# 设置随机种子
RANDOM_STATE = 42


# 1. 数据加载与合并
def load_and_merge_data(good_path, bad_path):
    # 读取CSV文件
    good_df = pd.read_csv(good_path)
    bad_df = pd.read_csv(bad_path)

    # 添加标签：1表示优质用户，0表示非优质用户
    good_df['label'] = 1
    bad_df['label'] = 0

    # 合并数据集
    data = pd.concat([good_df, bad_df], axis=0).reset_index(drop=True)

    print("合并后的数据集样本数:", data.shape[0])
    print("标签分布:\n", data['label'].value_counts())

    return data


# 2. 数据清洗与预处理
def preprocess_data(data):

    # a. 编码分类变量 'part' 使用独热编码
    data = pd.get_dummies(data, columns=['part'], drop_first=True)

    # b. 移除不必要的列 'username'
    data = data.drop(['username'], axis=1)

    # 确保 'year' 是数值类型
    data['year'] = data['year'].astype(int)

    return data


# 3. 特征工程
def feature_engineering(data):
    # a. 创建衍生特征
    data['likes_per_fan'] = data['likes'] / (data['fans'] + 1)  # 避免除以零
    data['coins_per_fan'] = data['coins'] / (data['fans'] + 1)
    data['collect_per_fan'] = data['collects'] / (data['fans'] + 1)
    data['total_interactions'] = data['likes'] + data['coins'] + data['collects']

    # 计算 'num_parts'（发布的视频分区数量）
    part_columns = [col for col in data.columns if 'part_' in col]
    data['num_parts'] = data[part_columns].sum(axis=1)

    # b. 标准化数值特征
    numerical_features = ['fans', 'likes', 'views', 'coins', 'collects', 'year',
                          'likes_per_fan', 'coins_per_fan', 'collect_per_fan',
                          'total_interactions', 'num_parts']

    scaler = StandardScaler()
    data[numerical_features] = scaler.fit_transform(data[numerical_features])

    return data, scaler


# 4. 处理类别不平衡（替代方法）
def random_oversample(X, y):
    # 合并特征和标签
    data = pd.concat([X, y], axis=1)

    # 分离多数类和少数类
    majority = data[data['label'] == 1]
    minority = data[data['label'] == 0]

    # 计算需要过采样的数量
    n_majority = majority.shape[0]
    n_minority = minority.shape[0]
    n_to_oversample = n_majority - n_minority

    # 随机复制少数类样本
    minority_oversampled = minority.sample(n=n_to_oversample, replace=True, random_state=42)

    # 合并数据
    data_oversampled = pd.concat([majority, minority, minority_oversampled], axis=0).reset_index(drop=True)

    # 分离特征和标签
    X_resampled = data_oversampled.drop(['label'], axis=1)
    y_resampled = data_oversampled['label']

    return X_resampled, y_resampled


# 5. 数据集划分
def split_data(features, labels):
    # 使用 train_test_split 进行划分，确保测试集有样本
    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.2,  # 20% 作为测试集
        random_state=42,
        stratify=labels  # 保持类别比例
    )

    print("\n训练集样本数:", X_train.shape[0])
    print("验证集样本数:", X_test.shape[0])

    return X_train, y_train, X_test, y_test


# 6. 模型训练与评估
def train_and_evaluate(X_train, y_train, X_test, y_test):
    # 初始化XGBoost模型
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.08,
        max_depth=5,
        scale_pos_weight=(len(y_train) - sum(y_train)) / sum(y_train),  # 处理类别不平衡
        use_label_encoder=False,
        eval_metric='auc',
        random_state=42
    )

    # 训练模型
    xgb_model.fit(X_train, y_train)

    # 预测
    y_pred = xgb_model.predict(X_test)
    y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]

    # 评估模型
    print("\n混淆矩阵:\n", confusion_matrix(y_test, y_pred))
    print("\n分类报告:\n", classification_report(y_test, y_pred))
    print("ROC AUC Score:", roc_auc_score(y_test, y_pred_proba))

    # 绘制ROC曲线
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'XGBoost (AUC = {roc_auc_score(y_test, y_pred_proba):.2f})')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.show()

    return xgb_model


# 7. 模型超参数调优（可选）
def hyperparameter_tuning(X_train, y_train):
    xgb_model = xgb.XGBClassifier(
        use_label_encoder=False,
        eval_metric='auc',
        random_state=42
    )

    param_grid = {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 1],
        'colsample_bytree': [0.8, 1],
        'scale_pos_weight': [(len(y_train) - sum(y_train)) / sum(y_train)]
    }

    grid_search = GridSearchCV(
        estimator=xgb_model,
        param_grid=param_grid,
        scoring='roc_auc',
        cv=3,
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X_train, y_train)

    print("\n最佳参数:", grid_search.best_params_)
    print("最佳 ROC AUC:", grid_search.best_score_)

    return grid_search.best_estimator_


# 8. 特征重要性可视化
def plot_feature_importance(model, feature_names):
    plt.figure(figsize=(12, 8))
    xgb.plot_importance(model, max_num_features=10)
    plt.title('Top 10 Feature Importances')
    plt.show()

# 9. 保存模型与Scaler
def save_model(model, scaler, model_path='xgb_model.pkl', scaler_path='scaler.pkl'):
    import joblib
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n模型已保存至 {model_path}")
    print(f"Scaler 已保存至 {scaler_path}")


# 预处理函数（测试）
def preprocess_new_user(new_user_df, scaler, training_features):

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


# 10. 主函数
def main():
    # 文件路径（请根据实际路径修改）
    good_path = 'user_detail.csv'
    bad_path = 'baduser_detail.csv'

    # 加载与合并数据
    data = load_and_merge_data(good_path, bad_path)

    # 预处理数据
    data = preprocess_data(data)

    # 特征工程
    data, scaler = feature_engineering(data)

    # 分离特征和标签
    features = data.drop(['label'], axis=1)
    labels = data['label']

    # 数据集划分
    X_train, y_train, X_test, y_test = split_data(features, labels)

    # 手动过采样
    X_train_res, y_train_res = random_oversample(X_train, y_train)
    print("\n过采样后的训练集标签分布:\n", pd.Series(y_train_res).value_counts())

    # 不进行额外的过采样或欠采样, 使用原始数据
    #X_train_res, y_train_res = X_train, y_train  # 保持原始数据

    # 模型训练与评估
    model = train_and_evaluate(X_train_res, y_train_res, X_test, y_test)
    # 新用户数据示例
    new_user = {
        'username': 'Lks',
        'year': 2021,
        'views': 10000000,
        'fans': 2983000,
        'likes': 5000000,
        'coins': 9475687,
        'collects': 5545783,
        'part': '生活'  # 请根据实际分类特征进行调整
    }

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
        print(f"用户 {new_user['username']} 是百大用户，预测概率为 {probability:.2f}")
    else:
        print(f"用户 {new_user['username']} 不是百大用户，预测概率为 {probability:.2f}")

    # 特征重要性可视化
    plot_feature_importance(model, X_train.columns)

    # 保存模型与Scaler
    save_model(model, scaler)


if __name__ == "__main__":
    main()
