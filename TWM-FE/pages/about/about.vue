<template>
  <view class="about-page">
    <!-- 导航栏 -->
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <image src="/static/icons/general/left.png" class="back-icon"></image>
      </view>
      <view class="nav-title">
        <text>关于我们</text>
      </view>
      <view class="nav-right"></view>
    </view>

    <!-- 关于内容 -->
    <scroll-view class="about-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 应用信息 -->
      <view class="app-info">
        <image src="/static/icons/general/dog.png" class="app-logo"></image>
        <text class="app-name">云游志</text>
        <text class="app-version">版本 1.1.0</text>
      </view>

      <!-- 公司介绍 -->
      <view class="company-section">
        <view class="section-header">
          <text class="section-title">公司简介</text>
        </view>
        <view class="company-content">
          <text class="company-text">
云游志是沃弥斯团队2025年开发的智慧旅游小程序，主要提供地图查看、说说分享、旅行计划制定、天气查询等功能。

团队成员由热爱旅行的同学组成，大家在技术、设计和策划上各展所长，一起探索如何让出行更简单、有趣。

我们坚持“用户至上”的理念，尽力为使用小程序的每一位朋友提供贴心的体验。愿你的每一次旅行，都能留下美好的回忆！
          </text>
        </view>
      </view>

      <!-- 旅行理念 -->
      <view class="culture-section">
        <view class="section-header">
          <text class="section-title">旅行理念</text>
        </view>
        <view class="culture-list">
          <view class="culture-item" v-for="(item, index) in cultureItems" :key="index">
            <view class="culture-icon">
              <image :src="item.icon" class="icon-img"></image>
            </view>
            <view class="culture-detail">
              <text class="culture-title">{{ item.title }}</text>
              <text class="culture-desc">{{ item.desc }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 旅行顾问 -->
      <view class="contact-section">
        <view class="section-header">
          <text class="section-title">旅行顾问</text>
        </view>
        <view class="contact-list">
          <view class="contact-item" @tap="makePhoneCall">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/phone.png" class="icon-img"></image>
              </view>
              <text class="item-text">紧急联络</text>
            </view>
            <text class="item-right">400-888-9999</text>
          </view>
          
          <view class="contact-item" @tap="sendEmail">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/email.png" class="icon-img"></image>
              </view>
              <text class="item-text">行程咨询</text>
            </view>
            <text class="item-right">travel@liuxing.com</text>
          </view>
          
          <view class="contact-item" @tap="visitWebsite">
            <view class="item-left">
              <view class="item-icon">
                <image src="/static/icons/general/web.png" class="icon-img"></image>
              </view>
              <text class="item-text">官方指南</text>
            </view>
            <text class="item-right">www.liuxingtravel.com</text>
          </view>
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
      appVersion: '2.1.0',
      companyIntro: `
云游志是沃弥斯团队2025年开发的智慧旅游小程序，主要提供地图查看、说说分享、旅行计划制定、天气查询等功能。

团队成员由热爱旅行的同学组成，大家在技术、设计和策划上各展所长，一起探索如何让出行更简单、有趣。

我们坚持“用户至上”的理念，尽力为使用小程序的每一位朋友提供贴心的体验。愿你的每一次旅行，都能留下美好的回忆！
      `,
      cultureItems: [
        {
          icon: '/static/icons/general/compass.png',
          title: '探索精神',
          desc: '发现世界之美，体验不同文化'
        },
        {
          icon: '/static/icons/general/heart.png',
          title: '用户至上',
          desc: '用心服务每一位旅行者'
        },
        {
          icon: '/static/icons/general/shield.png',
          title: '安全第一',
          desc: '全程保障旅行安全'
        }
      ],
      scrollHeight: 0
    }
  },
  onLoad() {
    this.calculateScrollHeight()
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
    
    // 返回上一页
    goBack() {
      const pages = getCurrentPages();
      if (pages.length > 1) {
        // 当页面栈中有多个页面时正常返回
        uni.navigateBack();
      } else {
        // 当页面栈中只有当前页面时，跳转到首页
        uni.reLaunch({
          url: '/pages/index/index' // 请根据实际项目结构调整首页路径
        });
	 }
 },	
    
    // 拨打电话
    makePhoneCall() {
      uni.makePhoneCall({
        phoneNumber: '4008889999'
      })
    },
    
    // 发送邮件
    sendEmail() {
      const email = 'travel@liuxing.com'
      uni.setClipboardData({
        data: email,
        success: () => {
          this.showToast('邮箱地址已复制到剪贴板')
        }
      })
    },
    
    // 访问网站
    visitWebsite() {
      const url = 'https://www.liuxingtravel.com'
      uni.setClipboardData({
        data: url,
        success: () => {
          this.showToast('网址已复制到剪贴板')
        }
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
/* 保持原有样式不变 */
.about-page {
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

/* 关于滚动区域 */
.about-scroll {
  flex: 1;
  background: #f8f8f8;
}

/* 应用信息 */
.app-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0 40rpx;
  background: #fff;
  margin-bottom: 20rpx;
}

.app-logo {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 20rpx;
}

.app-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 10rpx;
}

.app-version {
  font-size: 26rpx;
  color: #999;
}

/* 公司介绍 */
.company-section {
  background: #fff;
  margin: 20rpx 0;
  padding: 0 30rpx;
}

.section-header {
  padding: 30rpx 0 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.company-content {
  padding: 20rpx 0;
}

.company-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
  white-space: pre-line;
}

/* 企业文化 */
.culture-section {
  background: #fff;
  margin: 20rpx 0;
  padding: 0 30rpx;
}

.culture-list {
  padding: 20rpx 0;
}

.culture-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f8f8f8;
}

.culture-item:last-child {
  border-bottom: none;
}

.culture-icon {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.icon-img {
  width: 40rpx;
  height: 40rpx;
}

.culture-detail {
  flex: 1;
}

.culture-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 8rpx;
}

.culture-desc {
  font-size: 26rpx;
  color: #666;
}

/* 联系方式 */
.contact-section {
  background: #fff;
  margin: 20rpx 0;
  padding: 0 30rpx;
}

.contact-list {
  padding: 20rpx 0;
}

.contact-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f8f8f8;
}

.contact-item:last-child {
  border-bottom: none;
}

.item-left {
  display: flex;
  align-items: center;
}

.item-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-text {
  font-size: 28rpx;
  color: #333;
}

.item-right {
  font-size: 26rpx;
  color: #666;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>