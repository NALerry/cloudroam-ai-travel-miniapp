<template>
  <view class="settings-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <image src="/static/icons/general/back.png" class="back-icon"></image>
      </view>
      <view class="nav-title">
        <text>系统设置</text>
      </view>
      <view class="nav-right"></view>
    </view>

    <!-- 设置内容 -->
    <scroll-view class="settings-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 隐私设置 -->
      <view class="settings-section">
        <view class="section-header">
          <text class="section-title">隐私设置</text>
        </view>
        <view class="settings-list">
          <view class="setting-item" @tap="navigateTo('privacy')">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/privacy.png" class="icon-img"></image>
              </view>
              <text class="item-text">隐私设置</text>
            </view>
            <image src="/static/icons/general/right.png" class="arrow-icon"></image>
          </view>
        </view>
      </view>

      <!-- 通知设置 -->
      <view class="settings-section">
        <view class="section-header">
          <text class="section-title">通知设置</text>
        </view>
        <view class="settings-list">
          <view class="setting-item">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/notice.png" class="icon-img"></image>
              </view>
              <text class="item-text">消息通知</text>
            </view>
            <switch :checked="notificationEnabled" @change="onNotificationChange" color="#b8d4ff" />
          </view>
        </view>
      </view>

      <!-- 存储设置 -->
      <view class="settings-section">
        <view class="section-header">
          <text class="section-title">存储设置</text>
        </view>
        <view class="settings-list">
          <view class="setting-item" @tap="clearCache">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/clean.png" class="icon-img"></image>
              </view>
              <text class="item-text">清理缓存</text>
            </view>
            <view class="item-right">
              <text class="cache-size">{{ cacheSize }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 关于 -->
      <view class="settings-section">
        <view class="section-header">
          <text class="section-title">关于与反馈</text>
        </view>
        <view class="settings-list">
          <view class="setting-item" @tap="navigateTo('about')">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/dog.png" class="icon-img"></image>
              </view>
              <text class="item-text">关于我们</text>
            </view>
            <image src="/static/icons/general/right.png" class="arrow-icon"></image>
          </view>
		  
          <view class="setting-item">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/version.png" class="icon-img"></image>
              </view>
              <text class="item-text">版本信息</text>
            </view>
            <text class="version-text">{{ appVersion }}</text>
          </view>
        </view>
      </view>

      <!-- 退出登录 -->
      <view class="logout-section">
        <view class="logout-btn" @tap="showLogoutConfirm">
          <text class="logout-text">退出登录</text>
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
      notificationEnabled: true,
      cacheSize: '125.6MB',
      appVersion: '1.0.0',
      isLoading: false,
      scrollHeight: 0
    }
  },
  onLoad() {
    this.initPage()
    this.calculateScrollHeight()
  },
  onShow() {
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
    
    // 初始化页面
    async initPage() {
      this.isLoading = true
      await Promise.all([
        this.loadSettings(),
        this.calculateCacheSize()
      ])
      this.isLoading = false
    },
    
    // 加载设置
    async loadSettings() {
      try {
        const notificationSetting = uni.getStorageSync('notification_setting')
        if (notificationSetting !== null) {
          this.notificationEnabled = notificationSetting
        }
      } catch (error) {
        console.error('加载设置失败:', error)
      }
    },
    
    // 返回上一页
    goBack() {
      uni.navigateBack()
    },
    
    // 导航到不同页面
    navigateTo(page) {
      const routeMap = {
        'privacy': '/pages/privacy/privacy',
        'about': '/pages/about/about'
      }
      
      if (routeMap[page]) {
        uni.navigateTo({
          url: routeMap[page]
        })
      } else {
        this.showToast('功能开发中')
      }
    },
    
    // 通知设置变更
    onNotificationChange(e) {
      this.notificationEnabled = e.detail.value
      uni.setStorageSync('notification_setting', this.notificationEnabled)
      this.updateNotificationSetting()
      this.showSuccess(this.notificationEnabled ? '通知已开启' : '通知已关闭')
    },
    
    // 更新通知设置到服务器
    async updateNotificationSetting() {
      try {
        // API调用
      } catch (error) {
        console.error('更新通知设置失败:', error)
      }
    },
    
    // 清理缓存
    clearCache() {
      uni.showModal({
        title: '清理缓存',
        content: `确定要清理 ${this.cacheSize} 的缓存文件吗？`,
        confirmColor: '#b8d4ff',
        success: (res) => {
          if (res.confirm) {
            this.performClearCache()
          }
        }
      })
    },
    
    // 执行清理缓存
    async performClearCache() {
      uni.showLoading({
        title: '清理中...',
        mask: true
      })
      
      try {
        await this.doClearCache()
        await this.calculateCacheSize()
        uni.hideLoading()
        this.showSuccess('清理完成')
      } catch (error) {
        uni.hideLoading()
        console.error('清理缓存失败:', error)
        this.showError('清理失败')
      }
    },
    
    // 执行清理操作
    async doClearCache() {
      return new Promise((resolve) => {
        setTimeout(() => {
          const keys = uni.getStorageInfoSync().keys
          const cacheKeys = keys.filter(key => key.startsWith('cache_'))
          cacheKeys.forEach(key => {
            uni.removeStorageSync(key)
          })
          resolve()
        }, 1500)
      })
    },
    
    // 计算缓存大小
    async calculateCacheSize() {
      try {
        const storageInfo = uni.getStorageInfoSync()
        const totalSize = storageInfo.keys.reduce((total, key) => {
          const data = uni.getStorageSync(key)
          return total + (data ? JSON.stringify(data).length : 0)
        }, 0)
        
        const sizeMB = (totalSize / (1024 * 1024)).toFixed(1)
        this.cacheSize = `${sizeMB}MB`
      } catch (error) {
        console.error('计算缓存大小失败:', error)
        this.cacheSize = '0.0MB'
      }
    },
    
    // 显示退出登录确认
    showLogoutConfirm() {
      uni.showModal({
        title: '退出登录',
        content: '确定要退出登录吗？',
        confirmColor: '#b8d4ff',
        success: (res) => {
          if (res.confirm) {
            this.logout()
          }
        }
      })
    },
    
    // 退出登录
    async logout() {
      uni.showLoading({
        title: '退出中...',
        mask: true
      })
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.clearUserData()
        uni.hideLoading()
        this.showSuccess('退出成功')
        
        setTimeout(() => {
          uni.reLaunch({
            url: '/pages/login/login'
          })
        }, 1500)
        
      } catch (error) {
        uni.hideLoading()
        console.error('退出登录失败:', error)
        this.showError('退出失败')
      }
    },
    
    // 清除用户数据
    clearUserData() {
      const clearKeys = [
        'user_info',
        'user_token',
        'notification_setting',
        'user_settings'
      ]
      clearKeys.forEach(key => {
        uni.removeStorageSync(key)
      })
    },
    
    // 显示成功提示
    showSuccess(message) {
      uni.showToast({
        title: message,
        icon: 'success',
        duration: 2000
      })
    },
    
    // 显示错误提示
    showError(message) {
      uni.showToast({
        title: message,
        icon: 'none',
        duration: 3000
      })
    },
    
    // 显示普通提示
    showToast(message) {
      uni.showToast({
        title: message,
        icon: 'none',
        duration: 2000
      })
    }
  }
}
</script>

<style scoped>
.settings-page {
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

/* 设置滚动区域 */
.settings-scroll {
  flex: 1;
  background: #f8f8f8;
}

.settings-section {
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
  align-items: center;
  flex: 1;
}

.item-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-img {
  width: 28rpx;
  height: 28rpx;
}

.item-text {
  font-size: 28rpx;
  color: #333;
}

.arrow-icon {
  width: 24rpx;
  height: 24rpx;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.cache-size {
  font-size: 24rpx;
  color: #999;
}

.version-text {
  font-size: 24rpx;
  color: #999;
}

/* 退出登录区域 */
.logout-section {
  padding: 40rpx 30rpx;
}

.logout-btn {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  text-align: center;
  border: 1rpx solid #eee;
}

.logout-text {
  font-size: 32rpx;
  color: #ff4444;
  font-weight: 500;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>