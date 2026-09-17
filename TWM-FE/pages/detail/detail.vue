<template>
  <view class="detail-page">
    <view class="detail-header">
      <view class="header-left" @tap="goBack">
        <uni-icons type="arrowleft" size="20" color="#333"></uni-icons>
        <text>返回</text>
      </view>
      <text class="header-title">详情</text>
      <view class="header-right"></view>
    </view>

    <scroll-view class="detail-content" scroll-y>
      <view class="content-card">
        <text class="detail-title">{{ detailData.title }}</text>
        <text class="detail-desc">{{ detailData.desc }}</text>
        
        <view class="detail-meta">
          <text class="meta-item">{{ detailData.type }}</text>
          <text class="meta-item">{{ detailData.time }}</text>
        </view>
        
        <image 
          class="detail-image" 
          :src="detailData.image" 
          mode="widthFix"
          v-if="detailData.image"
        ></image>
        
        <text class="detail-content-text">
          {{ detailData.content }}
        </text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      detailData: {
        title: '',
        desc: '',
        type: '',
        time: '',
        image: '',
        content: '这里是详细的内容信息...'
      }
    }
  },
  onLoad(options) {
    if (options.title) {
      this.detailData.title = decodeURIComponent(options.title)
    }
    // 根据id加载详细数据
    this.loadDetailData(options.id)
  },
  methods: {
    async loadDetailData(id) {
      // 模拟加载详情数据
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 这里可以根据id从API获取数据
      this.detailData.desc = `关于"${this.detailData.title}"的详细内容`
      this.detailData.type = '攻略'
      this.detailData.time = '2024-01-15'
      this.detailData.image = '/static/search/strategy.jpg'
    },
    
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.detail-page {
  height: 100vh;
  background: #f8f8f8;
  display: flex;
  flex-direction: column;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 28rpx;
  color: #333;
}

.header-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.detail-content {
  flex: 1;
  padding: 30rpx;
}

.content-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.detail-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
  line-height: 1.4;
}

.detail-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  display: block;
  margin-bottom: 30rpx;
}

.detail-meta {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.meta-item {
  font-size: 24rpx;
  color: #FF6A00;
  background: #FFF0E6;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.detail-image {
  width: 100%;
  border-radius: 12rpx;
  margin-bottom: 30rpx;
}

.detail-content-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.8;
}
</style>