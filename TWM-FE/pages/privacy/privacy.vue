<template>
  <view class="privacy-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <image src="/static/icons/general/back.png" class="back-icon"></image>
      </view>
      <view class="nav-title">
        <text>隐私设置</text>
      </view>
      <view class="nav-right"></view>
    </view>

    <!-- 隐私设置内容 -->
    <scroll-view class="privacy-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 隐私政策开关 -->
      <view class="privacy-section">
        <view class="section-header">
          <text class="section-title">隐私保护设置</text>
        </view>
        <view class="settings-list">
          <view class="setting-item">
            <view class="item-left">
              <text class="item-text">个性化推荐</text>
              <text class="item-desc">根据您的使用习惯推荐内容</text>
            </view>
            <switch :checked="personalizedEnabled" @change="onPersonalizedChange" color="#b8d4ff" />
          </view>
          
          <view class="setting-item">
            <view class="item-left">
              <text class="item-text">数据收集</text>
              <text class="item-desc">收集使用数据以改进服务</text>
            </view>
            <switch :checked="dataCollectionEnabled" @change="onDataCollectionChange" color="#b8d4ff" />
          </view>
        </view>
      </view>

      <!-- 隐私政策 -->
      <view class="policy-section">
        <view class="section-header">
          <text class="section-title">隐私政策</text>
        </view>
        <view class="policy-content">
          <text class="policy-text">
            {{ privacyPolicy }}
          </text>
        </view>
        <view class="policy-footer">
          <text class="update-time">最后更新时间：{{ policyUpdateTime }}</text>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
data() {
  return {
    privacyPolicy: `
### 旅行隐私政策

**1. 我们收集的信息**
- 位置信息：用于推荐附近景点和路线规划
- 旅行偏好：记录您的出行方式、住宿偏好等个性化设置
- 支付信息：处理旅游产品预订和支付
- 身份信息：用于实名认证和行程单生成

**2. 信息使用方式**
- 为您提供个性化的旅行推荐和行程规划
- 完成旅游产品的预订、支付和售后服务
- 发送重要行程通知和安全提醒
- 优化我们的服务质量和用户体验

**3. 信息共享**
- 与合作的航空公司、酒店、景区共享必要的预订信息
- 在法律要求或保护用户权益时披露信息
- 经您明确同意后共享特定信息

**4. 数据安全**
- 采用加密技术保护您的支付信息
- 严格限制员工访问权限
- 定期进行安全审计和漏洞检测

**5. 您的权利**
- 随时查看、更正或删除您的个人信息
- 关闭位置服务或个性化推荐
- 撤回已授权的信息使用许可

**6. 政策更新**
- 政策变更时将通过应用内通知
- 重大变更将提前征求用户意见
    `,
    policyUpdateTime: '2023年11月1日'
  }
},
  onLoad() {
    this.calculateScrollHeight()
    this.loadSettings()
  },
  onResize() {
    this.calculateScrollHeight()
  },
  methods: {
    // 计算滚动区域高度
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      
      // 计算可用高度
      let availableHeight = windowHeight - statusBarHeight - navigationBarHeight
      this.scrollHeight = availableHeight
    },
    
    // 加载设置
    loadSettings() {
      try {
        const personalizedSetting = uni.getStorageSync('personalized_setting')
        const collectionSetting = uni.getStorageSync('collection_setting')
        
        if (personalizedSetting !== null) {
          this.personalizedEnabled = personalizedSetting
        }
        
        if (collectionSetting !== null) {
          this.dataCollectionEnabled = collectionSetting
        }
      } catch (error) {
        console.error('加载隐私设置失败:', error)
      }
    },
    
    // 返回上一页
    goBack() {
      uni.navigateBack()
    },
    
    // 个性化推荐变更
    onPersonalizedChange(e) {
      this.personalizedEnabled = e.detail.value
      uni.setStorageSync('personalized_setting', this.personalizedEnabled)
      this.showSuccess(this.personalizedEnabled ? '个性化推荐已开启' : '个性化推荐已关闭')
    },
    
    // 数据收集变更
    onDataCollectionChange(e) {
      this.dataCollectionEnabled = e.detail.value
      uni.setStorageSync('collection_setting', this.dataCollectionEnabled)
      this.showSuccess(this.dataCollectionEnabled ? '数据收集已开启' : '数据收集已关闭')
    },
    
    // 显示成功提示
    showSuccess(message) {
      uni.showToast({
        title: message,
        icon: 'success',
        duration: 2000
      })
    }
  }
}
</script>

<style scoped>
.privacy-page {
  min-height: 100vh;
  background-color: #f8f8f8;
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.nav-bar {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30rpx;
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
  position: relative;
}

.nav-left, .nav-right {
  width: 80rpx;
}

.back-icon {
  width: 32rpx;
  height: 32rpx;
}

.nav-title {
  flex: 1;
  text-align: center;
}

.nav-title text {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

/* 隐私设置滚动区域 */
.privacy-scroll {
  flex: 1;
  background: #f8f8f8;
}

.privacy-section {
  background: #fff;
  margin: 20rpx 0;
  border-radius: 0;
}

.section-header {
  padding: 30rpx 30rpx 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

/* 设置列表样式 */
.settings-list {
  background: #fff;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 30rpx;
  border-bottom: 1rpx solid #f8f8f8;
}

.setting-item:last-child {
  border-bottom: none;
}

.item-left {
  display: flex;
  flex-direction: column;
}

.item-text {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.item-desc {
  font-size: 24rpx;
  color: #999;
}

/* 隐私政策区域 */
.policy-section {
  background: #fff;
  margin: 20rpx 0;
  padding: 0 30rpx;
}

.policy-content {
  padding: 20rpx 0;
  line-height: 1.6;
}

.policy-text {
  font-size: 26rpx;
  color: #666;
  white-space: pre-line;
}

.policy-footer {
  padding: 20rpx 0;
  border-top: 1rpx solid #f0f0f0;
}

.update-time {
  font-size: 24rpx;
  color: #999;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>