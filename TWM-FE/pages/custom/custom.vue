<template>
  <view class="custom-page">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'festival' }"
        @tap="switchTab('festival')"
      >
        <text class="nav-text">节日</text>
      </view>
      <view 
        class="nav-item" 
        :class="{ active: currentTab === 'taboo' }"
        @tap="switchTab('taboo')"
      >
        <text class="nav-text">禁忌</text>
      </view>
    </view>

    <!-- 内容区域 -->
    <view class="content-section">
      <!-- 节日内容 -->
      <view class="tab-content" v-if="currentTab === 'festival'">
        <scroll-view class="content-scroll" scroll-y>
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索节日名称或国家" 
                v-model="festivalKeyword"
                @confirm="searchFestival"
              />
            </view>
          </view>
          
          <!-- 节日列表 -->
          <view class="festival-list">
            <view 
              class="festival-card" 
              v-for="item in filteredFestivals" 
              :key="item.id"
              @tap="viewFestivalDetail(item)"
            >
              <view class="festival-image">
                <image :src="item.image" mode="aspectFill"></image>
                <view class="country-tag">{{ item.country }}</view>
              </view>
              <view class="festival-info">
                <view class="festival-header">
                  <text class="festival-name">{{ item.name }}</text>
                  <text class="festival-date">{{ item.date }}</text>
                </view>
                <text class="festival-desc">{{ item.description }}</text>
                <view class="festival-tags">
                  <text 
                    class="tag" 
                    v-for="(tag, index) in item.tags" 
                    :key="index"
                  >{{ tag }}</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 禁忌内容 -->
      <view class="tab-content" v-if="currentTab === 'taboo'">
        <scroll-view class="content-scroll" scroll-y>
          <!-- 搜索区域 -->
          <view class="search-box">
            <view class="search-input">
              <image class="search-icon" src="/static/icons/general/search1.png"></image>
              <input 
                type="text" 
                placeholder="搜索国家或禁忌内容" 
                v-model="tabooKeyword"
                @confirm="searchTaboo"
              />
            </view>
          </view>
          
          <!-- 禁忌列表 -->
          <view class="taboo-list">
            <view 
              class="taboo-card" 
              v-for="item in filteredTaboos" 
              :key="item.id"
              @tap="viewTabooDetail(item)"
            >
              <view class="taboo-header">
                <view class="country-info">
                  <image class="country-flag" :src="item.flag"></image>
                  <text class="country-name">{{ item.country }}</text>
                </view>
                <view class="importance" :class="item.importance">
                  {{ item.importance === 'high' ? '重要' : item.importance === 'medium' ? '中等' : '一般' }}
                </view>
              </view>
              <view class="taboo-content">
                <text class="taboo-title">{{ item.title }}</text>
                <text class="taboo-desc">{{ item.description }}</text>
              </view>
              <view class="taboo-tips">
                <text class="tip-item" v-for="(tip, index) in item.tips" :key="index">
                  {{ tip }}
                </text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentTab: 'festival', // 当前选中的标签
      festivalKeyword: '', // 节日搜索关键词
      tabooKeyword: '', // 禁忌搜索关键词
      
      // 节日数据
      festivals: [
        {
          id: 1,
          name: '圣诞节',
          country: '西方国家',
          date: '12月25日',
          description: '圣诞节是基督教纪念耶稣诞生的重要节日，现已成为许多国家的公共假日。',
          image: '/static/images/custom/christmas.jpg',
          tags: ['宗教', '家庭', '礼物']
        },
        {
          id: 2,
          name: '春节',
          country: '中国',
          date: '农历正月初一',
          description: '春节是中国最重要的传统节日，象征着团圆和新的开始。',
          image: '/static/images/custom/spring-festival.jpg',
          tags: ['传统', '团圆', '烟花']
        },
        {
          id: 3,
          name: '排灯节',
          country: '印度',
          date: '每年10月或11月',
          description: '排灯节是印度教的重要节日，象征着光明战胜黑暗，知识战胜无知。',
          image: '/static/images/custom/diwali.jpg',
          tags: ['宗教', '光明', '庆祝']
        },
        {
          id: 4,
          name: '开斋节',
          country: '伊斯兰国家',
          date: '伊斯兰教历10月1日',
          description: '开斋节是伊斯兰教的重要节日，标志着斋月的结束。',
          image: '/static/images/custom/eid.jpg',
          tags: ['宗教', '斋戒', '家庭']
        },
        {
          id: 5,
          name: '亡灵节',
          country: '墨西哥',
          date: '11月1日-2日',
          description: '亡灵节是墨西哥的重要传统节日，用于纪念已故的亲人。',
          image: '/static/images/custom/day-of-dead.jpg',
          tags: ['传统', '纪念', '彩色']
        },
        {
          id: 6,
          name: '樱花节',
          country: '日本',
          date: '3月下旬至4月上旬',
          description: '樱花节是日本欣赏樱花盛开的重要季节，人们会举行花见活动。',
          image: '/static/images/custom/cherry-blossom.jpg',
          tags: ['自然', '赏花', '季节']
        }
      ],
      
      // 禁忌数据
      taboos: [
        {
          id: 1,
          country: '泰国',
          flag: '/static/images/flags/thailand.png',
          title: '头部禁忌',
          description: '在泰国，头部被视为身体最神圣的部位，不要触摸他人的头部，即使是小孩子。',
          importance: 'high',
          tips: ['不要摸别人的头', '不要用脚指向他人', '尊重僧侣']
        },
        {
          id: 2,
          country: '印度',
          flag: '/static/images/flags/india.png',
          title: '饮食禁忌',
          description: '在印度，牛被视为神圣的动物，许多印度教徒不吃牛肉。左手被认为是不洁的，避免用左手传递食物。',
          importance: 'high',
          tips: ['避免吃牛肉', '用右手传递食物', '尊重宗教场所']
        },
        {
          id: 3,
          country: '日本',
          flag: '/static/images/flags/japan.png',
          title: '礼仪禁忌',
          description: '在日本，筷子不能垂直插在饭中，这类似于葬礼仪式。进入家中或某些场所需要脱鞋。',
          importance: 'medium',
          tips: ['不要竖插筷子', '进入室内要脱鞋', '公共场所保持安静']
        },
        {
          id: 4,
          country: '中东国家',
          flag: '/static/images/flags/middle-east.png',
          title: '行为禁忌',
          description: '在中东许多国家，公开场合的亲密行为被视为不适当，特别是未婚男女之间。',
          importance: 'high',
          tips: ['避免公开亲密行为', '女性穿着要保守', '尊重宗教习俗']
        },
        {
          id: 5,
          country: '意大利',
          flag: '/static/images/flags/italy.png',
          title: '用餐禁忌',
          description: '在意大利，用餐时不要把面包倒置放在桌子上，这被认为会带来坏运气。',
          importance: 'low',
          tips: ['面包不要倒放', '用餐时不要早退', '品尝当地葡萄酒']
        },
        {
          id: 6,
          country: '俄罗斯',
          flag: '/static/images/flags/russia.png',
          title: '送礼禁忌',
          description: '在俄罗斯，送偶数数量的鲜花通常与葬礼相关，应避免。空花瓶也被认为会带来坏运气。',
          importance: 'medium',
          tips: ['送花要送奇数', '不要送空花瓶', '握手时要摘下手套']
        }
      ]
    }
  },
  
  computed: {
    // 过滤后的节日列表
    filteredFestivals() {
      if (!this.festivalKeyword) {
        return this.festivals
      }
      const keyword = this.festivalKeyword.toLowerCase()
      return this.festivals.filter(item => 
        item.name.toLowerCase().includes(keyword) || 
        item.country.toLowerCase().includes(keyword) ||
        item.tags.some(tag => tag.toLowerCase().includes(keyword))
      )
    },
    
    // 过滤后的禁忌列表
    filteredTaboos() {
      if (!this.tabooKeyword) {
        return this.taboos
      }
      const keyword = this.tabooKeyword.toLowerCase()
      return this.taboos.filter(item => 
        item.country.toLowerCase().includes(keyword) || 
        item.title.toLowerCase().includes(keyword) ||
        item.description.toLowerCase().includes(keyword)
      )
    }
  },
  
  methods: {
    // 切换标签
    switchTab(tab) {
      this.currentTab = tab
    },
    
    // 搜索节日
    searchFestival() {
      // 搜索逻辑已在计算属性中实现
      uni.showToast({
        title: '搜索完成',
        icon: 'success'
      })
    },
    
    // 搜索禁忌
    searchTaboo() {
      // 搜索逻辑已在计算属性中实现
      uni.showToast({
        title: '搜索完成',
        icon: 'success'
      })
    },
    
    // 查看节日详情
    viewFestivalDetail(item) {
      uni.navigateTo({
        url: `/pages/custom/festival-detail?id=${item.id}`
      })
    },
    
    // 查看禁忌详情
    viewTabooDetail(item) {
      uni.navigateTo({
        url: `/pages/custom/taboo-detail?id=${item.id}`
      })
    }
  },
  
  onLoad(options) {
    // 处理URL参数，设置默认标签页
    if (options.tab) {
      this.currentTab = options.tab;
    }
  }
}
</script>

<style scoped>
.custom-page {
  height: 100vh;
  background: linear-gradient(135deg, #f0f6ff 0%, #e8ecff 100%);
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.nav-bar {
  display: flex;
  background-color: #fff;
  border-bottom: 1rpx solid #e0e8ff;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2rpx 10rpx rgba(184, 212, 255, 0.2);
}

.nav-item {
  flex: 1;
  text-align: center;
  padding: 30rpx 0;
  position: relative;
}

.nav-text {
  font-size: 32rpx;
  color: #666;
  font-weight: 500;
  transition: all 0.3s;
}

.nav-item.active .nav-text {
  color: #4a86e8;
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 80rpx;
  height: 6rpx;
  background-color: #4a86e8;
  border-radius: 3rpx;
}

/* 内容区域样式 */
.content-section {
  flex: 1;
  overflow: hidden;
}

.tab-content {
  height: 100%;
}

.content-scroll {
  height: 100%;
}

/* 搜索框样式 */
.search-box {
  padding: 30rpx;
  background-color: #fff;
  border-bottom: 1rpx solid #eee;
}

.search-input {
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 50rpx;
  padding: 20rpx 30rpx;
}

.search-icon {
  width: 36rpx;
  height: 36rpx;
  margin-right: 20rpx;
}

.search-input input {
  flex: 1;
  font-size: 28rpx;
}

/* 节日列表样式 */
.festival-list {
  padding: 0 30rpx 30rpx;
}

.festival-card {
  background-color: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-top: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.festival-image {
  position: relative;
  height: 300rpx;
}

.festival-image image {
  width: 100%;
  height: 100%;
}

.country-tag {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.festival-info {
  padding: 30rpx;
}

.festival-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.festival-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.festival-date {
  font-size: 26rpx;
  color: #999;
}

.festival-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  margin-bottom: 20rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.festival-tags {
  display: flex;
  flex-wrap: wrap;
}

.tag {
  background-color: #f0f7ff;
  color: #4a86e8;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  margin-right: 15rpx;
  margin-bottom: 10rpx;
}

/* 禁忌列表样式 */
.taboo-list {
  padding: 0 30rpx 30rpx;
}

.taboo-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-top: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.taboo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.country-info {
  display: flex;
  align-items: center;
}

.country-flag {
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  margin-right: 15rpx;
}

.country-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.importance {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #fff;
}

.importance.high {
  background-color: #ff6b6b;
}

.importance.medium {
  background-color: #ffa726;
}

.importance.low {
  background-color: #66bb6a;
}

.taboo-content {
  margin-bottom: 20rpx;
}

.taboo-title {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 15rpx;
}

.taboo-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
}

.taboo-tips {
  display: flex;
  flex-wrap: wrap;
}

.tip-item {
  background-color: #fff3e0;
  color: #ff9800;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  margin-right: 15rpx;
  margin-bottom: 10rpx;
  border: 1rpx solid #ffe0b2;
}
</style>