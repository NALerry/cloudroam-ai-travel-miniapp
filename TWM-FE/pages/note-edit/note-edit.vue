<template>
  <view class="page-container">
    <!-- 页面头部 -->
    <view class="page-header">
      <view class="header-nav">
        <view class="nav-btn" @tap="goBack">
          <image src="/static/icons/general/back.png" class="nav-icon"></image>
        </view>
        <text class="header-title">{{ isEdit ? '编辑笔记' : '新建笔记' }}</text>
        <view class="nav-btn" @tap="saveNote">
          <text class="save-text">保存</text>
        </view>
      </view>
    </view>

    <!-- 内容区域 -->
    <scroll-view class="content-scroll" scroll-y :style="{height: scrollHeight + 'px'}">
      <view class="edit-form">
        <!-- 标题 -->
        <view class="form-group">
          <text class="form-label">标题</text>
          <input 
            class="form-input" 
            v-model="noteForm.title" 
            placeholder="请输入笔记标题"
            maxlength="50"
          />
          <text class="input-count">{{ noteForm.title.length }}/50</text>
        </view>

        <!-- 地点 -->
        <view class="form-group">
          <text class="form-label">地点</text>
          <input 
            class="form-input" 
            v-model="noteForm.location" 
            placeholder="请输入地点"
            maxlength="30"
          />
        </view>

        <!-- 日期 -->
        <view class="form-group">
          <text class="form-label">日期</text>
          <picker 
            mode="date" 
            :value="noteForm.date" 
            @change="onDateChange"
          >
            <view class="picker-input">
              <text :class="noteForm.date ? 'picker-text' : 'picker-placeholder'">
                {{ noteForm.date || '请选择日期' }}
              </text>
              <image src="/static/icons/general/calendar.png" class="picker-icon"></image>
            </view>
          </picker>
        </view>

        <!-- 内容 -->
        <view class="form-group">
          <text class="form-label">内容</text>
          <textarea 
            class="form-textarea" 
            v-model="noteForm.content" 
            placeholder="记录您的旅行体验..."
            maxlength="1000"
          ></textarea>
          <text class="input-count">{{ noteForm.content.length }}/1000</text>
        </view>

        <!-- 图片上传 -->
        <view class="form-group">
          <text class="form-label">图片</text>
          <view class="image-uploader">
            <view 
              class="upload-item" 
              v-for="(image, index) in noteForm.images" 
              :key="index"
            >
              <image :src="image" class="upload-image" mode="aspectFill"></image>
              <view class="image-remove" @tap="removeImage(index)">
                <image src="/static/icons/general/close.png" class="remove-icon"></image>
              </view>
            </view>
            <view class="upload-btn" @tap="chooseImage" v-if="noteForm.images.length < 9">
              <image src="/static/icons/general/add.png" class="upload-icon"></image>
              <text class="upload-text">添加图片</text>
            </view>
          </view>
        </view>

        <!-- 标签 -->
        <view class="form-group">
          <text class="form-label">标签</text>
          <view class="tags-input">
            <input 
              class="tag-input" 
              v-model="newTag" 
              placeholder="输入标签后按回车"
              maxlength="10"
              @confirm="addTag"
            />
            <view class="tags-list">
              <view 
                class="tag-item" 
                v-for="(tag, index) in noteForm.tags" 
                :key="index"
              >
                <text class="tag-text">{{ tag }}</text>
                <view class="tag-remove" @tap="removeTag(index)">
                  <image src="/static/icons/general/close.png" class="tag-remove-icon"></image>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <!-- 删除按钮 -->
      <view class="delete-section" v-if="isEdit">
        <view class="delete-btn" @tap="deleteNote">
          <text class="delete-text">删除笔记</text>
        </view>
      </view>

      <!-- 底部安全区域 -->
      <view class="safe-area"></view>
    </scroll-view>

    <!-- 加载状态 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-content">
        <image src="/static/icons/general/loading.png" class="loading-icon"></image>
        <text class="loading-text">保存中...</text>
      </view>
    </view>
  </view>
</template>

<script>
import { formatDate } from '@/utils/date.js'

export default {
  data() {
    return {
      noteForm: {
        id: null,
        title: '',
        location: '',
        date: formatDate(new Date()),
        content: '',
        images: [],
        tags: [],
        createTime: ''
      },
      newTag: '',
      isEdit: false,
      loading: false,
      scrollHeight: 0
    }
  },
  onLoad(options) {
    this.calculateScrollHeight()
    if (options.id) {
      this.isEdit = true
      this.loadNoteData(options.id)
    } else {
      this.noteForm.createTime = new Date().toISOString()
    }
  },
  methods: {
    calculateScrollHeight() {
      const systemInfo = uni.getSystemInfoSync()
      const windowHeight = systemInfo.windowHeight
      const statusBarHeight = systemInfo.statusBarHeight || 0
      const navigationBarHeight = 44
      this.scrollHeight = windowHeight - statusBarHeight - navigationBarHeight
    },
    
    loadNoteData(id) {
      try {
        const notes = uni.getStorageSync('travel_notes') || []
        const note = notes.find(n => n.id == id)
        if (note) {
          this.noteForm = { ...note }
        } else {
          uni.showToast({
            title: '笔记不存在',
            icon: 'none'
          })
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (error) {
        console.error('加载笔记数据失败:', error)
        uni.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    onDateChange(e) {
      this.noteForm.date = e.detail.value
    },
    
    async chooseImage() {
      try {
        const res = await uni.chooseImage({
          count: 9 - this.noteForm.images.length,
          sizeType: ['compressed'],
          sourceType: ['album', 'camera']
        })
        
        this.noteForm.images = [...this.noteForm.images, ...res.tempFilePaths]
      } catch (error) {
        console.error('选择图片失败:', error)
      }
    },
    
    removeImage(index) {
      this.noteForm.images.splice(index, 1)
    },
    
    addTag() {
      if (this.newTag.trim() && this.noteForm.tags.length < 5) {
        this.noteForm.tags.push(this.newTag.trim())
        this.newTag = ''
      }
    },
    
    removeTag(index) {
      this.noteForm.tags.splice(index, 1)
    },
    
    async saveNote() {
      if (!this.validateForm()) return
      
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        const notes = uni.getStorageSync('travel_notes') || []
        
        if (this.isEdit) {
          // 更新现有笔记
          const index = notes.findIndex(n => n.id == this.noteForm.id)
          if (index !== -1) {
            notes[index] = { ...this.noteForm }
          }
        } else {
          // 创建新笔记
          const newNote = {
            ...this.noteForm,
            id: Date.now(),
            createTime: new Date().toISOString()
          }
          notes.unshift(newNote)
        }
        
        uni.setStorageSync('travel_notes', notes)
        
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
        
      } catch (error) {
        console.error('保存笔记失败:', error)
        uni.showToast({
          title: '保存失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    validateForm() {
      if (!this.noteForm.title.trim()) {
        uni.showToast({
          title: '请输入标题',
          icon: 'none'
        })
        return false
      }
      
      if (!this.noteForm.content.trim()) {
        uni.showToast({
          title: '请输入内容',
          icon: 'none'
        })
        return false
      }
      
      return true
    },
    
    deleteNote() {
      uni.showModal({
        title: '删除笔记',
        content: '确定要删除这篇笔记吗？此操作不可恢复。',
        confirmColor: '#ff4444',
        success: (res) => {
          if (res.confirm) {
            this.performDeleteNote()
          }
        }
      })
    },
    
    async performDeleteNote() {
      this.loading = true
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        
        const notes = uni.getStorageSync('travel_notes') || []
        const filteredNotes = notes.filter(n => n.id != this.noteForm.id)
        uni.setStorageSync('travel_notes', filteredNotes)
        
        uni.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
        
      } catch (error) {
        console.error('删除笔记失败:', error)
        uni.showToast({
          title: '删除失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: #f8f8f8;
}

/* 页面头部 */
.page-header {
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
  padding: 0 30rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.header-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.nav-btn {
  padding: 16rpx;
}

.nav-icon {
  width: 32rpx;
  height: 32rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.save-text {
  font-size: 32rpx;
  color: #2c6be8;
  font-weight: 500;
}

/* 内容区域 */
.content-scroll {
  background: #f8f8f8;
}

.edit-form {
  background: #fff;
  margin-bottom: 20rpx;
  border-radius: 0;
}

.form-group {
  padding: 30rpx;
  border-bottom: 1rpx solid #f8f8f8;
}

.form-group:last-child {
  border-bottom: none;
}

.form-label {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

.form-input {
  font-size: 28rpx;
  color: #333;
  padding: 20rpx 0;
  width: 100%;
}

.input-count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  display: block;
  margin-top: 16rpx;
}

.picker-input {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 0;
}

.picker-text {
  font-size: 28rpx;
  color: #333;
}

.picker-placeholder {
  font-size: 28rpx;
  color: #999;
}

.picker-icon {
  width: 28rpx;
  height: 28rpx;
  opacity: 0.5;
}

.form-textarea {
  font-size: 28rpx;
  color: #333;
  width: 100%;
  height: 200rpx;
  line-height: 1.6;
}

/* 图片上传 */
.image-uploader {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.upload-item {
  position: relative;
  width: 160rpx;
  height: 160rpx;
}

.upload-image {
  width: 100%;
  height: 100%;
  border-radius: 8rpx;
}

.image-remove {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 40rpx;
  height: 40rpx;
  background: #ff4444;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #fff;
}

.remove-icon {
  width: 20rpx;
  height: 20rpx;
}

.upload-btn {
  width: 160rpx;
  height: 160rpx;
  border: 2rpx dashed #ddd;
  border-radius: 8rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-icon {
  width: 48rpx;
  height: 48rpx;
  margin-bottom: 16rpx;
  opacity: 0.5;
}

.upload-text {
  font-size: 24rpx;
  color: #999;
}

/* 标签输入 */
.tags-input {
  margin-top: 20rpx;
}

.tag-input {
  font-size: 28rpx;
  color: #333;
  padding: 20rpx;
  background: #f8f8f8;
  border-radius: 8rpx;
  margin-bottom: 20rpx;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag-item {
  display: flex;
  align-items: center;
  background: #e8f1ff;
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
}

.tag-text {
  font-size: 24rpx;
  color: #2c6be8;
  margin-right: 8rpx;
}

.tag-remove {
  width: 24rpx;
  height: 24rpx;
  border-radius: 12rpx;
  background: #2c6be8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-remove-icon {
  width: 12rpx;
  height: 12rpx;
}

/* 删除按钮 */
.delete-section {
  padding: 40rpx 30rpx;
}

.delete-btn {
  background: #fff;
  border-radius: 16rpx;
  padding: 28rpx;
  text-align: center;
  border: 1rpx solid #ff4444;
}

.delete-text {
  font-size: 32rpx;
  color: #ff4444;
  font-weight: 500;
}

/* 加载状态和底部安全区域样式与旅行笔记页面相同 */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  background: #fff;
  padding: 40rpx;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
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
  color: #666;
}

.safe-area {
  height: env(safe-area-inset-bottom);
  background: #f8f8f8;
}
</style>