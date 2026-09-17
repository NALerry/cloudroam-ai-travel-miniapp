<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <view class="header-back" @tap="goBack">
          <image src="/static/icons/general/back.png" class="back-icon" mode="aspectFit"></image>
        </view>
        <text class="header-title">路线详情</text>
        <view class="header-actions">
          <view class="action-btn share" @tap="shareRoute">
            <image src="/static/icons/general/share.png" class="action-icon" mode="aspectFit"></image>
          </view>
        </view>
      </view>
      <view class="header-bg"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <!-- 路线图片 -->
      <view class="route-image-section">
        <image class="route-image" :src="routeData.image" mode="aspectFill"></image>
        <view class="route-tags">
          <view class="route-tag" v-for="tag in routeData.tags" :key="tag">
            <text>{{ tag }}</text>
          </view>
        </view>
        <view class="favorite-btn" @tap="toggleRouteFavorite">
          <image 
            class="favorite-icon" 
            :src="routeData.isFavorite ? '/static/icons/general/heart-filled.png' : '/static/icons/general/heart.png'" 
            mode="aspectFit"
          ></image>
        </view>
      </view>

      <!-- 路线基本信息 -->
      <view class="form-section">
        <view class="form-card">
          <view class="route-header">
            <text class="route-title">{{ routeData.title }}</text>
            <view class="route-rating">
              <image class="star-icon" src="/static/icons/general/star.png" mode="aspectFit"></image>
              <text class="rating-score">{{ routeData.rating }}</text>
            </view>
          </view>

          <view class="route-meta">
            <view class="meta-item">
              <image class="meta-icon" src="/static/icons/route/time.png" mode="aspectFit"></image>
              <text class="meta-text">{{ routeData.duration }}</text>
            </view>
            <view class="meta-item">
              <image class="meta-icon" src="/static/icons/route/distance.png" mode="aspectFit"></image>
              <text class="meta-text">{{ routeData.distance }}</text>
            </view>
            <view class="meta-item">
              <image class="meta-icon" src="/static/icons/route/cost.png" mode="aspectFit"></image>
              <text class="meta-text">¥{{ routeData.cost }}/人</text>
            </view>
          </view>

          <view class="route-desc">
            <text class="desc-text">{{ routeData.description }}</text>
          </view>

          <view class="route-highlights">
            <text class="highlights-title">路线亮点：</text>
            <text class="highlights-text">{{ routeData.highlights.join(' · ') }}</text>
          </view>

          <view class="route-stats">
            <view class="stat-item">
              <text class="stat-value">{{ routeData.collectedCount }}</text>
              <text class="stat-label">收藏</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ routeData.completedCount }}</text>
              <text class="stat-label">完成</text>
            </view>
            <view class="stat-item">
              <text class="stat-value">{{ routeData.recommendCount }}</text>
              <text class="stat-label">推荐</text>
            </view>
          </view>

          <view class="route-author">
            <image class="author-avatar" :src="routeData.author.avatar" mode="aspectFill"></image>
            <text class="author-name">{{ routeData.author.name }}</text>
            <text class="author-badge" v-if="routeData.author.isOfficial">官方</text>
          </view>
        </view>
      </view>

      <!-- 行程安排 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/gps.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">行程安排</text>
        </view>

        <view class="form-card">
          <view class="timeline">
            <view 
              class="timeline-item" 
              v-for="(day, index) in routeData.itinerary" 
              :key="index"
              :class="{ active: expandedDay === index }"
            >
              <view class="timeline-header" @tap="toggleDayExpand(index)">
                <view class="day-info">
                  <text class="day-number">第{{ index + 1 }}天</text>
                  <text class="day-title">{{ day.title }}</text>
                </view>
                <view class="day-meta">
                  <text class="day-distance">{{ day.distance }}</text>
                  <image 
                    class="expand-icon" 
                    :src="expandedDay === index ? '/static/icons/general/up.png' : '/static/icons/general/down.png'" 
                    mode="aspectFit"
                  ></image>
                </view>
              </view>
              
              <view class="timeline-content" v-if="expandedDay === index">
                <view class="places-list">
                  <view 
                    class="place-item" 
                    v-for="(place, placeIndex) in day.places" 
                    :key="placeIndex"
                  >
                    <view class="place-order">
                      <text class="order-text">{{ placeIndex + 1 }}</text>
                    </view>
                    <view class="place-info">
                      <text class="place-name">{{ place.name }}</text>
                      <text class="place-desc">{{ place.description }}</text>
                      <view class="place-time">
                        <image class="time-icon" src="/static/icons/route/time.png" mode="aspectFit"></image>
                        <text class="time-text">{{ place.time }}</text>
                      </view>
                    </view>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 费用明细 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/cost.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">费用明细</text>
        </view>

        <view class="form-card">
          <view class="cost-list">
            <view class="cost-item" v-for="(item, index) in routeData.costDetails" :key="index">
              <text class="cost-name">{{ item.name }}</text>
              <text class="cost-value">¥{{ item.value }}</text>
            </view>
          </view>
          <view class="cost-total">
            <text class="total-label">总计</text>
            <text class="total-value">¥{{ routeData.cost }}</text>
          </view>
        </view>
      </view>

      <!-- 温馨提示 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/tip.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">温馨提示</text>
        </view>

        <view class="form-card">
          <view class="tips-list">
            <view class="tip-item" v-for="(tip, index) in routeData.tips" :key="index">
              <text class="tip-text">{{ tip }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 用户评价 -->
      <view class="form-section">
        <view class="section-title">
          <image src="/static/icons/general/comment.png" class="section-icon" mode="aspectFit"></image>
          <text class="section-title-text">用户评价</text>
          <text class="section-subtitle">({{ routeData.comments.length }})</text>
        </view>

        <view class="form-card">
          <view class="comments-list">
            <view 
              class="comment-item" 
              v-for="(comment, index) in routeData.comments.slice(0, 3)" 
              :key="index"
            >
              <view class="comment-header">
                <image class="comment-avatar" :src="comment.avatar" mode="aspectFill"></image>
                <view class="comment-user">
                  <text class="user-name">{{ comment.name }}</text>
                  <view class="comment-rating">
                    <image 
                      class="star-icon" 
                      src="/static/icons/general/star.png" 
                      mode="aspectFit"
                      v-for="n in 5"
                      :key="n"
                      :style="{ opacity: n <= comment.rating ? 1 : 0.3 }"
                    ></image>
                  </view>
                </view>
                <text class="comment-date">{{ comment.date }}</text>
              </view>
              <text class="comment-text">{{ comment.text }}</text>
            </view>
          </view>
          
          <view class="view-all-comments" @tap="viewAllComments" v-if="routeData.comments.length > 3">
            <text class="view-all-text">查看全部{{ routeData.comments.length }}条评价</text>
            <image class="right-icon" src="/static/icons/general/right.png" mode="aspectFit"></image>
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 底部操作区域 -->
    <view class="bottom-actions">
      <view class="action-buttons">
        <view class="action-btn favorite" @tap="toggleRouteFavorite">
          <image 
            class="action-icon" 
            :src="routeData.isFavorite ? '/static/icons/general/heart-filled.png' : '/static/icons/general/heart.png'" 
            mode="aspectFit"
          ></image>
          <text class="btn-text">{{ routeData.isFavorite ? '已收藏' : '收藏' }}</text>
        </view>
        <view class="action-btn start" @tap="startRoute">
          <text class="btn-text">开始路线</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      routeId: null,
      scrollHeight: 0,
      expandedDay: 0, // 默认展开第一天
      
      routeData: {
        id: 1,
        title: '北京经典三日游',
        description: '涵盖故宫、天坛、颐和园等经典景点的深度文化之旅',
        duration: '3天2晚',
        distance: '25公里',
        cost: '800',
        rating: 4.8,
        image: '/static/images/routes/beijing-classic.jpg',
        tags: ['经典', '文化', '家庭游'],
        highlights: ['故宫深度讲解', '天坛祭天仪式体验', '颐和园皇家园林'],
        collectedCount: 2456,
        completedCount: 1890,
        recommendCount: 98,
        isFavorite: false,
        author: {
          name: '北京旅游局',
          avatar: '/static/images/avatars/official.png',
          isOfficial: true
        },
        itinerary: [
          {
            title: '天安门广场 - 故宫博物院 - 景山公园',
            distance: '8公里',
            places: [
              {
                name: '天安门广场',
                description: '观看升旗仪式，感受国家象征的庄严',
                time: '早上6:00-8:00'
              },
              {
                name: '故宫博物院',
                description: '探索明清两代的皇家宫殿，了解中国古代建筑艺术',
                time: '上午8:30-12:00'
              },
              {
                name: '景山公园',
                description: '登高俯瞰故宫全景，拍摄最佳照片',
                time: '下午2:00-4:00'
              }
            ]
          },
          {
            title: '天坛公园 - 前门大街 - 王府井',
            distance: '10公里',
            places: [
              {
                name: '天坛公园',
                description: '参观明清皇帝祭天场所，了解古代祭祀文化',
                time: '早上8:00-11:00'
              },
              {
                name: '前门大街',
                description: '品尝北京传统小吃，体验老北京商业文化',
                time: '中午11:30-13:30'
              },
              {
                name: '王府井步行街',
                description: '购物休闲，感受现代北京商业氛围',
                time: '下午2:30-5:00'
              }
            ]
          },
          {
            title: '颐和园 - 圆明园',
            distance: '7公里',
            places: [
              {
                name: '颐和园',
                description: '游览中国现存最完整的皇家园林，欣赏昆明湖美景',
                time: '早上8:30-12:00'
              },
              {
                name: '圆明园遗址',
                description: '参观历史遗迹，了解中国近代史',
                time: '下午1:30-4:00'
              }
            ]
          }
        ],
        costDetails: [
          { name: '交通费用', value: '200' },
          { name: '门票费用', value: '300' },
          { name: '餐饮费用', value: '200' },
          { name: '其他费用', value: '100' }
        ],
        tips: [
          '建议提前在官方网站预约故宫门票，避免排队',
          '天安门广场升旗时间随日出时间变化，请提前查询',
          '颐和园面积较大，建议穿着舒适的鞋子',
          '前门大街小吃众多，可以品尝炸酱面、豆汁等地道美食'
        ],
        comments: [
          {
            name: '旅行爱好者',
            avatar: '/static/images/avatars/user1.jpg',
            rating: 5,
            date: '2023-10-15',
            text: '这条路线安排得非常合理，三天时间刚好能游览完北京的主要景点，导游讲解也很专业。'
          },
          {
            name: '文化探索者',
            avatar: '/static/images/avatars/user2.jpg',
            rating: 4,
            date: '2023-09-28',
            text: '特别喜欢故宫和天坛的深度讲解，让我对中国古代文化有了更深入的了解。'
          },
          {
            name: '家庭游客',
            avatar: '/static/images/avatars/user3.jpg',
            rating: 5,
            date: '2023-09-10',
            text: '带着孩子一起走的这条路线，孩子对皇家建筑特别感兴趣，收获很大。'
          }
        ]
      }
    }
  },
  onLoad(options) {
    this.routeId = options.id
    this.calculateScrollHeight()
    this.loadRouteData()
  },
  onReady() {
    this.calculateScrollHeight()
  },
  onShow() {
    this.$nextTick(() => {
      this.calculateScrollHeight()
    })
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const headerHeight = 160 / 750 * systemInfo.windowWidth
      const bottomHeight = 120 / 750 * systemInfo.windowWidth
      const safeArea = systemInfo.safeAreaInsets ? systemInfo.safeAreaInsets.bottom : 0
      
      this.scrollHeight = windowHeight - headerHeight - bottomHeight - safeArea
    },
    
    loadRouteData() {
      // 在实际应用中，这里应该根据routeId从API或本地存储加载数据
      // 这里使用模拟数据
      console.log('加载路线数据，ID:', this.routeId)
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    toggleDayExpand(index) {
      this.expandedDay = this.expandedDay === index ? -1 : index
    },
    
    toggleRouteFavorite() {
      this.routeData.isFavorite = !this.routeData.isFavorite
      uni.showToast({
        title: this.routeData.isFavorite ? '已收藏路线' : '已取消收藏',
        icon: 'success'
      })
    },
    
    shareRoute() {
      uni.showActionSheet({
        itemList: ['分享给好友', '分享到朋友圈', '复制链接'],
        success: (res) => {
          console.log('分享选项:', res.tapIndex)
          uni.showToast({
            title: '分享成功',
            icon: 'success'
          })
        }
      })
    },
    
    startRoute() {
      uni.showModal({
        title: '开始路线',
        content: '确定要开始这条路线吗？',
        success: (res) => {
          if (res.confirm) {
            uni.navigateTo({
              url: `/pages/route/navigation?id=${this.routeId}`
            })
          }
        }
      })
    },
    
    viewAllComments() {
      uni.navigateTo({
        url: `/pages/route/comments?id=${this.routeId}`
      })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

/* 页面头部 */
.page-header {
  position: relative;
  height: 160rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

.header-content {
  position: relative;
  z-index: 2;
  padding: 80rpx 30rpx 20rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  width: 24rpx;
  height: 24rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #2c5282;
  text-shadow: 0 2rpx 8rpx rgba(255, 255, 255, 0.5);
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  text-align: center;
}

.header-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
}

.action-icon {
  width: 28rpx;
  height: 28rpx;
}

/* 内容区域 */
.content-scroll {
  margin-top: -20rpx;
  border-top-left-radius: 40rpx;
  border-top-right-radius: 40rpx;
  background: #f0f7ff;
  position: relative;
  z-index: 3;
}

/* 路线图片 */
.route-image-section {
  position: relative;
  height: 400rpx;
}

.route-image {
  width: 100%;
  height: 100%;
}

.route-tags {
  position: absolute;
  top: 20rpx;
  left: 20rpx;
  display: flex;
  gap: 10rpx;
}

.route-tag {
  background: rgba(184, 212, 255, 0.9);
  color: #fff;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.favorite-btn {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  width: 60rpx;
  height: 60rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.favorite-icon {
  width: 28rpx;
  height: 28rpx;
}

/* 表单区域 */
.form-section {
  background: transparent;
  margin: 24rpx;
}

.section-title {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  flex-wrap: wrap;
}

.section-icon {
  width: 32rpx;
  height: 32rpx;
  margin-right: 12rpx;
  opacity: 0.8;
}

.section-title-text {
  font-size: 30rpx;
  font-weight: 700;
  color: #2c5282;
  margin-right: 16rpx;
}

.section-subtitle {
  font-size: 24rpx;
  color: #5a7ca8;
  font-weight: 400;
}

.form-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  box-shadow: 0 6rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
}

/* 路线基本信息 */
.route-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20rpx;
}

.route-title {
  flex: 1;
  font-size: 36rpx;
  color: #2c5282;
  font-weight: 700;
  line-height: 1.4;
  margin-right: 15rpx;
}

.route-rating {
  display: flex;
  align-items: center;
  gap: 6rpx;
  flex-shrink: 0;
}

.star-icon {
  width: 24rpx;
  height: 24rpx;
}

.rating-score {
  font-size: 26rpx;
  color: #ffb300;
  font-weight: 600;
}

.route-meta {
  display: flex;
  gap: 30rpx;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.meta-icon {
  width: 28rpx;
  height: 28rpx;
}

.meta-text {
  font-size: 24rpx;
  color: #5a7ca8;
  font-weight: 500;
}

.route-desc {
  margin-bottom: 20rpx;
}

.desc-text {
  font-size: 28rpx;
  color: #2c5282;
  line-height: 1.5;
}

.route-highlights {
  background: #f8fbff;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.highlights-title {
  font-size: 24rpx;
  color: #b8d4ff;
  font-weight: 600;
  margin-bottom: 8rpx;
  display: block;
}

.highlights-text {
  font-size: 26rpx;
  color: #2c5282;
  line-height: 1.4;
}

.route-stats {
  display: flex;
  gap: 40rpx;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.stat-value {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 700;
}

.stat-label {
  font-size: 22rpx;
  color: #5a7ca8;
}

.route-author {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.author-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
}

.author-name {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 500;
}

.author-badge {
  background: #b8d4ff;
  color: #fff;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
}

/* 行程安排 */
.timeline {
  position: relative;
}

.timeline-item {
  margin-bottom: 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #f8fbff;
  border: 1rpx solid #e1edff;
  transition: all 0.3s ease;
}

.timeline-item.active {
  background: #ffffff;
  box-shadow: 0 4rpx 16rpx rgba(184, 212, 255, 0.4);
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
}

.day-info {
  flex: 1;
}

.day-number {
  font-size: 24rpx;
  color: #b8d4ff;
  font-weight: 600;
  display: block;
  margin-bottom: 6rpx;
}

.day-title {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

.day-meta {
  display: flex;
  align-items: center;
  gap: 15rpx;
}

.day-distance {
  font-size: 24rpx;
  color: #5a7ca8;
}

.expand-icon {
  width: 24rpx;
  height: 24rpx;
}

.timeline-content {
  padding: 0 24rpx 24rpx;
}

.places-list {
  border-top: 1rpx solid #e1edff;
  padding-top: 20rpx;
}

.place-item {
  display: flex;
  margin-bottom: 20rpx;
  padding: 20rpx;
  background: #ffffff;
  border-radius: 12rpx;
  border: 1rpx solid #e1edff;
}

.place-item:last-child {
  margin-bottom: 0;
}

.place-order {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #b8d4ff;
  border-radius: 50%;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.order-text {
  font-size: 24rpx;
  color: #ffffff;
  font-weight: 600;
}

.place-info {
  flex: 1;
}

.place-name {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.place-desc {
  font-size: 24rpx;
  color: #5a7ca8;
  line-height: 1.4;
  display: block;
  margin-bottom: 12rpx;
}

.place-time {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.time-icon {
  width: 20rpx;
  height: 20rpx;
}

.time-text {
  font-size: 22rpx;
  color: #5a7ca8;
}

/* 费用明细 */
.cost-list {
  margin-bottom: 20rpx;
}

.cost-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.cost-item:last-child {
  border-bottom: none;
}

.cost-name {
  font-size: 26rpx;
  color: #2c5282;
}

.cost-value {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 600;
}

.cost-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0 0;
  border-top: 2rpx solid #e1edff;
}

.total-label {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

.total-value {
  font-size: 32rpx;
  color: #ff6b6b;
  font-weight: 700;
}

/* 温馨提示 */
.tips-list {
  padding: 0;
}

.tip-item {
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.tip-item:last-child {
  border-bottom: none;
}

.tip-text {
  font-size: 26rpx;
  color: #2c5282;
  line-height: 1.5;
}

/* 用户评价 */
.comments-list {
  margin-bottom: 20rpx;
}

.comment-item {
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.comment-avatar {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  margin-right: 16rpx;
}

.comment-user {
  flex: 1;
}

.user-name {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 500;
  display: block;
  margin-bottom: 6rpx;
}

.comment-rating {
  display: flex;
  gap: 4rpx;
}

.comment-date {
  font-size: 22rpx;
  color: #5a7ca8;
}

.comment-text {
  font-size: 26rpx;
  color: #2c5282;
  line-height: 1.5;
}

.view-all-comments {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  background: #f8fbff;
  border-radius: 12rpx;
  border: 1rpx solid #e1edff;
}

.view-all-text {
  font-size: 26rpx;
  color: #2c5282;
  font-weight: 500;
  margin-right: 12rpx;
}

.right-icon {
  width: 20rpx;
  height: 20rpx;
}

/* 底部操作区域 */
.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #f0f7ff;
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #e1edff;
  z-index: 10;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24rpx;
  border-radius: 16rpx;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-btn:active {
  transform: scale(0.98);
}

.action-btn.favorite {
  background: #ffffff;
  border: 2rpx solid #b8d4ff;
  color: #2c5282;
}

.action-btn.start {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border: 2rpx solid #8bb9ff;
  color: #2c5282;
  box-shadow: 0 4rpx 12rpx rgba(139, 185, 255, 0.4);
}

.action-btn.favorite .btn-text {
  margin-left: 8rpx;
}

.btn-text {
  font-size: 28rpx;
  font-weight: 600;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f0f7ff;
}
</style>