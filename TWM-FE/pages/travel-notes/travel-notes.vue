<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-content">
        <text class="header-title">旅行笔记</text>
        <text class="header-subtitle">记录旅行中的点点滴滴</text>
      </view>
      <view class="header-bg"></view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}" @refresherrefresh="onRefresh" refresher-enabled>
      <!-- 新建笔记按钮 -->
      <view class="create-section">
        <view class="create-card">
          <view class="create-header">
            <image src="/static/icons/general/edit.png" class="create-icon"></image>
            <text class="create-title">新建旅行笔记</text>
          </view>
          <text class="create-desc">记录您的旅行故事与美好瞬间</text>
          <view class="create-btn" @tap="createNote">
            <text class="create-btn-text">开始记录</text>
            <image src="/static/icons/general/right.png" class="create-arrow"></image>
          </view>
        </view>
      </view>

      <!-- 笔记列表 -->
      <view class="list-section" v-if="notes.length > 0">
        <view class="section-header">
          <view class="section-title-wrapper">
            <image src="/static/icons/general/book.png" class="section-icon"></image>
            <text class="section-title">我的旅行笔记</text>
          </view>
          <text class="section-count">{{ notes.length }}篇笔记</text>
        </view>
        
        <view class="note-list">
          <view 
            class="note-card" 
            v-for="note in notes" 
            :key="note.id"
            @tap="viewNoteDetail(note.id)"
          >
            <view class="card-header">
              <view class="note-basic">
                <text class="note-title">{{ note.title }}</text>
                <view class="note-status" :class="note.status || 'completed'">
                  {{ getStatusText(note.status) }}
                </view>
              </view>
              <view class="note-date-badge">
                <text class="date-text">{{ formatDate(note.date) }}</text>
              </view>
            </view>
            
            <view class="note-info">
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/gps.png" class="info-icon"></image>
                  <text class="info-text">{{ note.location }}</text>
                </view>
              </view>
              <view class="info-row">
                <view class="info-item">
                  <image src="/static/icons/general/calendar.png" class="info-icon"></image>
                  <text class="info-text">{{ formatRelativeTime(note.createTime) }}</text>
                </view>
              </view>
            </view>
            
            <view class="note-content">
              <view class="note-images" v-if="note.images && note.images.length > 0">
                <image 
                  v-for="(img, index) in note.images.slice(0, 3)" 
                  :key="index"
                  :src="img" 
                  class="note-image"
                  mode="aspectFill"
                ></image>
                <view class="image-count" v-if="note.images.length > 3">
                  +{{ note.images.length - 3 }}
                </view>
              </view>
              
              <view class="note-preview">
                <text class="preview-text">{{ note.content }}</text>
              </view>
            </view>
            
            <view class="card-footer">
              <view class="note-meta">
                <text class="meta-text">创建于 {{ formatDate(note.createTime) }}</text>
              </view>
              <view class="note-actions">
                <view class="action-btn edit" @tap.stop="editNote(note.id)">
                  <image src="/static/icons/general/edit.png" class="action-icon"></image>
                  <text class="action-text">编辑</text>
                </view>
                <view class="action-btn delete" @tap.stop="deleteNote(note.id)">
                  <image src="/static/icons/general/delete.png" class="action-icon"></image>
                  <text class="action-text">删除</text>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else>
        <view class="empty-content">
          <image src="/static/icons/general/book.png" class="empty-icon"></image>
          <text class="empty-title">暂无旅行笔记</text>
          <text class="empty-desc">记录您的第一次旅行体验</text>
          <view class="empty-btn" @tap="createNote">
            <text class="empty-btn-text">创建第一篇笔记</text>
          </view>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 加载状态 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-content">
        <image src="/static/icons/general/loading.png" class="loading-icon"></image>
        <text class="loading-text">加载中...</text>
      </view>
    </view>
  </view>
</template>

<script>
import { formatRelativeTime, formatDate } from '@/utils/date.js'

export default {
  data() {
    return {
      notes: [],
      loading: false,
      scrollHeight: 0
    }
  },
  onLoad() {
    this.calculateScrollHeight()
    this.loadNotes()
  },
  onShow() {
    // 当从编辑页面返回时刷新数据
    this.loadNotes()
  },
  onResize() {
    this.calculateScrollHeight()
  },
  onPullDownRefresh() {
    this.loadNotes()
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight - 120
    },
    
    async loadNotes() {
      this.loading = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 从本地存储获取数据
        const savedNotes = uni.getStorageSync('travel_notes') || []
        this.notes = savedNotes.map(note => ({
          ...note,
          // 确保日期格式正确
          createTime: note.createTime || new Date().toISOString(),
          date: note.date || formatDate(new Date()),
          status: note.status || 'completed' // 默认状态为已完成
        }))
      } catch (error) {
        console.error('加载笔记失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
        uni.stopPullDownRefresh()
      }
    },
    
    onRefresh() {
      this.loadNotes()
    },
    
    createNote() {
      uni.navigateTo({
        url: '/pages/note-edit/note-edit'
      })
    },
    
    editNote(id) {
      uni.navigateTo({
        url: `/pages/note-edit/note-edit?id=${id}`
      })
    },
    
    viewNoteDetail(id) {
      uni.navigateTo({
        url: `/pages/note-detail/note-detail?id=${id}`
      })
    },
    
    deleteNote(id) {
      uni.showModal({
        title: '删除笔记',
        content: '确定要删除这篇笔记吗？此操作不可恢复。',
        confirmColor: '#ff6b6b',
        success: (res) => {
          if (res.confirm) {
            this.performDeleteNote(id)
          }
        }
      })
    },
    
    async performDeleteNote(id) {
      try {
        this.notes = this.notes.filter(note => note.id !== id)
        uni.setStorageSync('travel_notes', this.notes)
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        })
      } catch (error) {
        console.error('删除笔记失败:', error)
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        })
      }
    },
    
    getStatusText(status) {
      const statusMap = {
        'draft': '草稿',
        'published': '已发布',
        'completed': '已完成',
        'archived': '已归档'
      }
      return statusMap[status] || '未知'
    },
    
    formatRelativeTime,
    formatDate
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
}

/* 页面头部 - 清新蓝色背景 */
.page-header {
  position: relative;
  height: 280rpx;
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
  padding: 80rpx 30rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header-title {
  font-size: 42rpx;
  font-weight: 700;
  color: #2c5282;
  margin-bottom: 16rpx;
  text-shadow: 0 2rpx 8rpx rgba(255, 255, 255, 0.5);
}

.header-subtitle {
  font-size: 28rpx;
  color: #4a7bb8;
  font-weight: 400;
}

/* 内容区域 */
.content-scroll {
  margin-top: -40rpx;
  border-top-left-radius: 40rpx;
  border-top-right-radius: 40rpx;
  background: #f0f7ff;
  position: relative;
  z-index: 3;
}

/* 新建笔记卡片 - 清新蓝色风格 */
.create-section {
  padding: 30rpx;
}

.create-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #d1e3ff;
}

.create-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.create-icon {
  width: 24rpx;
  height: 24rpx;
  margin-right: 16rpx;
}

.create-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #2c5282;
}

.create-desc {
  font-size: 26rpx;
  color: #5a7ca8;
  margin-bottom: 32rpx;
  line-height: 1.5;
}

.create-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #b8d4ff 0%, #bcc4e8 100%);
  border-radius: 16rpx;
  padding: 24rpx 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(139, 185, 255, 0.4);
}

.create-btn-text {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

.create-arrow {
  width: 24rpx;
  height: 24rpx;
}

/* 笔记列表 - 清新蓝色风格 */
.list-section {
  background: transparent;
  margin-bottom: 20rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30rpx 24rpx;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
}

.section-icon {
  width: 28rpx;
  height: 28rpx;
  margin-right: 12rpx;
  opacity: 0.8;
}

.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #2c5282;
}

.section-count {
  font-size: 26rpx;
  color: #5a7ca8;
  background: rgba(184, 212, 255, 0.5);
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;
}

.note-list {
  padding: 0 30rpx;
}

.note-card {
  background: #ffffff;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
  transition: all 0.3s ease;
}

.note-card:active {
  transform: translateY(2rpx);
  box-shadow: 0 2rpx 12rpx rgba(184, 212, 255, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.note-basic {
  flex: 1;
}

.note-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #2c5282;
  display: block;
  margin-bottom: 12rpx;
  line-height: 1.3;
}

.note-status {
  display: inline-block;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-weight: 500;
  margin-left: 12rpx;
}

.note-status.draft {
  background: rgba(184, 212, 255, 0.3);
  color: #2c5282;
  border: 1rpx solid #b8d4ff;
}

.note-status.published {
  background: rgba(255, 193, 7, 0.2);
  color: #e6a700;
  border: 1rpx solid #ffc107;
}

.note-status.completed {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
  border: 1rpx solid #4caf50;
}

.note-status.archived {
  background: rgba(97, 97, 97, 0.1);
  color: #616161;
  border: 1rpx solid #cccccc;
}

.note-date-badge {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  padding: 8rpx 16rpx;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(139, 185, 255, 0.3);
}

.date-text {
  font-size: 22rpx;
  color: #2c5282;
  font-weight: 600;
}

.note-info {
  margin-bottom: 20rpx;
}

.info-row {
  margin-bottom: 12rpx;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-icon {
  width: 20rpx;
  height: 20rpx;
  margin-right: 12rpx;
  opacity: 0.6;
}

.info-text {
  font-size: 26rpx;
  color: #5a7ca8;
}

.note-content {
  margin-bottom: 24rpx;
}

.note-images {
  display: flex;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.note-image {
  width: 120rpx;
  height: 120rpx;
  border-radius: 8rpx;
}

.image-count {
  width: 120rpx;
  height: 120rpx;
  border-radius: 8rpx;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
}

.note-preview {
  padding: 20rpx;
  background: #f8fbff;
  border-radius: 12rpx;
  border-left: 4rpx solid #b8d4ff;
}

.preview-text {
  font-size: 26rpx;
  color: #5a7ca8;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid #e1edff;
}

.note-meta {
  flex: 1;
}

.meta-text {
  font-size: 24rpx;
  color: #a0bcd8;
}

.note-actions {
  display: flex;
  gap: 16rpx;
}

.action-btn {
  display: flex;
  align-items: center;
  padding: 12rpx 20rpx;
  border-radius: 12rpx;
  transition: all 0.3s ease;
}

.action-btn.edit {
  background: rgba(184, 212, 255, 0.3);
  border: 1rpx solid #b8d4ff;
}

.action-btn.delete {
  background: rgba(255, 107, 107, 0.1);
  border: 1rpx solid #ff6b6b;
}

.action-btn:active {
  transform: scale(0.95);
}

.action-icon {
  width: 20rpx;
  height: 20rpx;
  margin-right: 8rpx;
}

.action-btn.edit .action-icon {
  opacity: 0.8;
}

.action-btn.delete .action-icon {
  opacity: 0.8;
}

.action-text {
  font-size: 24rpx;
  font-weight: 500;
}

.action-btn.edit .action-text {
  color: #2c5282;
}

.action-btn.delete .action-text {
  color: #ff6b6b;
}

/* 空状态 */
.empty-state {
  background: transparent;
  padding: 120rpx 60rpx;
}

.empty-content {
  text-align: center;
  background: #ffffff;
  padding: 80rpx 40rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 24rpx rgba(184, 212, 255, 0.3);
  border: 1rpx solid #e1edff;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 32rpx;
  opacity: 0.5;
}

.empty-title {
  font-size: 32rpx;
  color: #2c5282;
  display: block;
  margin-bottom: 16rpx;
  font-weight: 600;
}

.empty-desc {
  font-size: 26rpx;
  color: #5a7ca8;
  display: block;
  margin-bottom: 40rpx;
  line-height: 1.5;
}

.empty-btn {
  background: linear-gradient(135deg, #b8d4ff 0%, #8bb9ff 100%);
  border-radius: 16rpx;
  padding: 24rpx 48rpx;
  display: inline-block;
  box-shadow: 0 4rpx 16rpx rgba(139, 185, 255, 0.4);
}

.empty-btn-text {
  font-size: 28rpx;
  color: #2c5282;
  font-weight: 600;
}

/* 加载状态 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(184, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: #ffffff;
  padding: 40rpx;
  border-radius: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 8rpx 32rpx rgba(184, 212, 255, 0.4);
  border: 1rpx solid #e1edff;
}

.loading-icon {
  width: 60rpx;
  height: 60rpx;
  margin-bottom: 20rpx;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 28rpx;
  color: #5a7ca8;
  font-weight: 500;
}

/* 安全区域 */
.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f0f7ff;
}
</style>