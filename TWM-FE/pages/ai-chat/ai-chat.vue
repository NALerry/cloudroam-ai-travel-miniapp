<template>
  <view class="ai-chat-page">
    <!-- 顶部导航栏 -->
    <view class="chat-header">
      <view class="header-left" @tap="goBack">
        <text class="back-icon">←</text>
        <text class="back-text">返回</text>
      </view>
      <view class="header-center">
        <image class="header-avatar" src="/static/avatars/Dog1.jpg" mode="aspectFit"></image>
        <view class="header-info">
          <text class="ai-name">AI Dog</text>
          <view class="status-badge" :class="{ 'online': isOnline }">
            <text class="ai-status">{{ aiStatusText }}</text>
          </view>
        </view>
      </view>
      <view class="header-right">
        <view class="more-actions" @tap="showMoreActions">
          <text class="more-icon">⋯</text>
        </view>
      </view>
    </view>

    <!-- 聊天内容区域 - 修复背景断层问题 -->
    <scroll-view 
      class="chat-content" 
      scroll-y 
      :scroll-top="scrollTop"
      scroll-with-animation
      @scrolltoupper="loadMoreHistory"
      :enable-back-to-top="true"
      :show-scrollbar="false"
    >
      <!-- 内部容器负责背景和内容 -->
      <view class="chat-messages-wrapper">
        <view class="chat-messages">
          <!-- 加载更多历史 -->
          <view class="loading-more" v-if="isLoadingHistory">
            <text>加载历史记录中...</text>
          </view>

          <!-- 欢迎消息 -->
          <view class="message-item ai-message" v-if="messages.length === 0">
            <view class="message-avatar ai-avatar">
              <image src="/static/avatars/Dog1.jpg" mode="aspectFit"></image>
            </view>
            <view class="message-content ai-content">
              <view class="message-bubble ai-bubble welcome-bubble">
                <text class="message-text">你好！我是你的AI Dog。今天有什么可以帮你的吗？</text>
              </view>
              <view class="suggest-questions">
                <view 
                  class="suggest-item" 
                  v-for="(question, index) in suggestQuestions" 
                  :key="index"
                  @tap="selectSuggestQuestion(question)"
                >
                  <text class="suggest-text">{{ question }}</text>
                </view>
              </view>
              <text class="message-time">{{ getCurrentTime() }}</text>
            </view>
          </view>

          <!-- 消息列表 -->
          <view 
            class="message-item" 
            :class="[message.sender === 'user' ? 'user-message' : 'ai-message']"
            v-for="(message, index) in messages" 
            :key="index"
          >
            <!-- AI头像（左侧） -->
            <view class="message-avatar" v-if="message.sender === 'ai'">
              <image src="/static/avatars/Dog1.jpg" mode="aspectFit"></image>
            </view>
            
            <!-- 消息内容区 -->
            <view class="message-content" :class="[message.sender === 'user' ? 'user-content' : 'ai-content']">
              <view class="message-bubble" :class="[message.sender === 'user' ? 'user-bubble' : 'ai-bubble']">
                <text class="message-text">{{ message.content }}</text>
              </view>
              
              <!-- 引用来源（仅AI消息） -->
              <view class="message-sources" v-if="message.sender === 'ai' && message.sources && message.sources.length > 0">
                <text class="source-label">来源：</text>
                <text class="source-text">{{ formatSources(message.sources) }}</text>
              </view>
              
              <!-- 反馈按钮（仅AI消息） -->
              <view class="feedback-buttons" v-if="message.sender === 'ai' && !message.feedbackGiven">
                <text class="feedback-icon helpful" @tap="submitFeedback(message, 1)">👍 有用</text>
                <text class="feedback-icon unhelpful" @tap="submitFeedback(message, 0)">👎 没用</text>
              </view>
              
              <text class="message-time">{{ message.time }}</text>
            </view>

            <!-- 用户头像（右侧） -->
            <view class="message-avatar user-avatar" v-if="message.sender === 'user'">
              <image :src="userAvatar" mode="aspectFit"></image>
            </view>
          </view>

          <!-- AI正在输入指示器 -->
          <view class="message-item ai-message" v-if="isAIThinking">
            <view class="message-avatar">
              <image src="/static/avatars/Dog1.jpg" mode="aspectFit"></image>
            </view>
            <view class="message-content ai-content">
              <view class="message-bubble ai-bubble typing-bubble">
                <view class="typing-indicator">
                  <text class="typing-text">AI 正在思考</text>
                  <view class="typing-dots">
                    <text class="dot">.</text>
                    <text class="dot">.</text>
                    <text class="dot">.</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
          
          <!-- 底部留白，确保滚动到底部时最后一条消息不被遮挡 -->
          <view class="bottom-spacer"></view>
        </view>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-section">
      <view class="input-container">
        <textarea 
          class="message-input" 
          v-model="inputMessage" 
          placeholder="输入你的问题..."
          :maxlength="500"
          :adjust-position="true"
          :auto-height="true"
          @confirm="sendMessage"
        ></textarea>
        <button 
          class="send-button" 
          :class="{ 'send-button-active': inputMessage.trim() }"
          @tap="sendMessage"
          :disabled="!inputMessage.trim() || isAIThinking"
        >
          <text class="send-icon">↑</text>
        </button>
      </view>
      
      <!-- 快捷操作 -->
      <view class="quick-actions">
        <scroll-view class="actions-scroll" scroll-x show-scrollbar="false">
          <view 
            class="action-item" 
            v-for="(action, index) in quickActions" 
            :key="index"
            @tap="selectQuickAction(action)"
          >
            <text class="action-text">{{ action.text }}</text>
          </view>
        </scroll-view>
      </view>
    </view>
    
    <!-- 悬浮按钮：新建对话 -->
    <view class="fab-button" @tap="createNewSessionAndClear">
      <text class="fab-icon">+</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      isAIThinking: false,
      scrollTop: 0,
      
      sessionId: null,
      userId: 'test_user_001',
      
      isOnline: true,
      aiStatusText: '在线',
      isLoadingHistory: false,
      
      userAvatar: '/static/avatars/default_avatar.png',
      
      suggestQuestions: [
        '如何查询订单状态？',
        '如何申请退款？',
        '配送时间要多久？',
        '如何联系人工客服？',
        '会员权益有哪些？',
        '优惠券怎么使用？'
      ],
      quickActions: [
        { text: '订单查询', type: 'order_query' },
        { text: '退款申请', type: 'refund' },
        { text: '物流追踪', type: 'logistics' },
        { text: '会员服务', type: 'member' },
        { text: '优惠活动', type: 'promotion' },
        { text: '投诉建议', type: 'complaint' }
      ]
    }
  },
  
  onLoad(options) {
    if (options.sessionId) {
      this.sessionId = options.sessionId
    }
    if (options.userId) {
      this.userId = options.userId
    }
    this.initChat()
  },
  
  onShow() {
    this.checkServiceHealth()
  },
  
  methods: {
    async initChat() {
      console.log('初始化AI助手...')
      uni.showLoading({ title: '加载中...' })
      
      try {
        if (this.sessionId) {
          await this.loadHistoryMessages()
        } else {
          const lastSession = uni.getStorageSync(`lastSession_${this.userId}`)
          if (lastSession) {
            this.sessionId = lastSession
            await this.loadHistoryMessages()
          } else {
            await this.createNewSession()
          }
        }
      } catch (error) {
        console.error('初始化失败:', error)
        await this.createNewSession()
      }
      
      uni.hideLoading()
      setTimeout(() => {
        this.scrollToBottom()
      }, 100)
    },
    
    async createNewSession() {
      return new Promise((resolve, reject) => {
        uni.request({
          url: 'http://localhost:8081/api/chat/session',
          method: 'POST',
          data: {
            userId: this.userId,
            title: '新对话'
          },
          header: { 'Content-Type': 'application/json' },
          success: (res) => {
            if (res.data.success) {
              this.sessionId = res.data.data.sessionId
              uni.setStorageSync(`lastSession_${this.userId}`, this.sessionId)
              this.messages = []
              resolve()
            } else {
              reject(new Error(res.data.error || '创建会话失败'))
            }
          },
          fail: (err) => {
            console.error('创建会话失败:', err)
            reject(err)
          }
        })
      })
    },
    
    async createNewSessionAndClear() {
      uni.showModal({
        title: '新建对话',
        content: '开始新对话？当前对话将被保存。',
        success: async (res) => {
          if (res.confirm) {
            await this.createNewSession()
            this.scrollToBottom()
            uni.showToast({ title: '已开始新对话', icon: 'success' })
          }
        }
      })
    },
    
    async loadHistoryMessages() {
      this.isLoadingHistory = true
      
      return new Promise((resolve, reject) => {
        uni.request({
          url: `http://localhost:8081/api/chat/history?userId=${this.userId}&sessionId=${this.sessionId}&limit=50`,
          method: 'GET',
          success: (res) => {
            if (res.data.success && res.data.data.messages) {
              const historyMessages = res.data.data.messages.map(msg => ({
                sender: msg.role === 'user' ? 'user' : 'ai',
                content: msg.content,
                time: this.formatTime(msg.created_at),
                sources: msg.sources || []
              }))
              this.messages = historyMessages
            }
            resolve()
          },
          fail: (err) => {
            console.error('加载历史记录失败:', err)
            reject(err)
          },
          complete: () => {
            this.isLoadingHistory = false
          }
        })
      })
    },
    
    checkServiceHealth() {
      uni.request({
        url: 'http://localhost:8081/health',
        method: 'GET',
        timeout: 5000,
        success: (res) => {
          if (res.data.status === 'ok') {
            this.isOnline = true
            this.aiStatusText = '在线'
          } else {
            this.isOnline = false
            this.aiStatusText = '离线'
          }
        },
        fail: () => {
          this.isOnline = false
          this.aiStatusText = '离线'
        }
      })
    },
    
    sendMessage() {
      const message = this.inputMessage.trim()
      if (!message || this.isAIThinking) return
      
      if (!this.isOnline) {
        uni.showToast({ title: '服务不可用，请稍后再试', icon: 'none' })
        return
      }
      
      const userMessage = {
        sender: 'user',
        content: message,
        time: this.getCurrentTime(),
        sources: []
      }
      this.messages.push(userMessage)
      this.inputMessage = ''
      this.scrollToBottom()
      
      this.isAIThinking = true
      
      uni.request({
        url: 'http://localhost:8081/api/chat/send',
        method: 'POST',
        data: {
          userId: this.userId,
          sessionId: this.sessionId,
          message: message
        },
        header: { 'Content-Type': 'application/json' },
        timeout: 60000,
        success: (res) => {
          if (res.data && res.data.success) {
            if (res.data.data.sessionId && !this.sessionId) {
              this.sessionId = res.data.data.sessionId
              uni.setStorageSync(`lastSession_${this.userId}`, this.sessionId)
            }
            
            const aiMessage = {
              sender: 'ai',
              content: res.data.data.content,
              time: this.getCurrentTime(),
              sources: res.data.data.sources || [],
              feedbackGiven: false
            }
            this.messages.push(aiMessage)
          } else {
            const errorMsg = res.data?.error || '服务器错误'
            this.messages.push({
              sender: 'ai',
              content: `抱歉，发生错误：${errorMsg}`,
              time: this.getCurrentTime(),
              sources: []
            })
          }
          this.isAIThinking = false
          this.scrollToBottom()
        },
        fail: (err) => {
          console.error('请求失败:', err)
          this.messages.push({
            sender: 'ai',
            content: '连接AI服务失败。请确保：\n1. Python服务器正在运行\n2. 端口8081可用\n3. 已勾选“不验证域名”',
            time: this.getCurrentTime(),
            sources: []
          })
          this.isAIThinking = false
          this.scrollToBottom()
        }
      })
    },
    
    submitFeedback(message, isHelpful) {
      const rating = isHelpful ? 5 : 1
      
      uni.request({
        url: 'http://localhost:8081/api/feedback',
        method: 'POST',
        data: {
          sessionId: this.sessionId,
          userId: this.userId,
          rating: rating,
          feedback: message.content.substring(0, 200)
        },
        success: () => {
          message.feedbackGiven = true
          uni.showToast({
            title: isHelpful ? '感谢你的反馈！' : '我们会努力改进',
            icon: 'none'
          })
        },
        fail: () => {
          uni.showToast({ title: '提交反馈失败', icon: 'none' })
        }
      })
    },
    
    selectSuggestQuestion(question) {
      this.inputMessage = question
      this.sendMessage()
    },
    
    selectQuickAction(action) {
      const actionMessages = {
        'order_query': '我想查询订单状态',
        'refund': '我想申请退款',
        'logistics': '我的包裹在哪里？',
        'member': '会员权益有哪些？',
        'promotion': '有什么优惠活动？',
        'complaint': '我需要联系客服'
      }
      this.inputMessage = actionMessages[action.type] || action.text
      this.sendMessage()
    },
    
    getCurrentTime() {
      const now = new Date()
      const hours = now.getHours().toString().padStart(2, '0')
      const minutes = now.getMinutes().toString().padStart(2, '0')
      return `${hours}:${minutes}`
    },
    
    formatTime(timestamp) {
      if (!timestamp) return this.getCurrentTime()
      const date = new Date(timestamp)
      return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    },
    
    formatSources(sources) {
      if (!sources || sources.length === 0) return ''
      const sourceNames = sources.map(s => s.source).filter((v, i, a) => a.indexOf(v) === i)
      return sourceNames.join(', ')
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        // 使用一个较大的值确保滚动到底部
        this.scrollTop = 99999
      })
    },
    
    loadMoreHistory() {
      // 可以在这里实现加载更多历史记录的逻辑
      console.log('滚动到顶部，加载更多历史记录')
    },
    
    goBack() {
      uni.navigateBack()
    },
    
    showMoreActions() {
      uni.showActionSheet({
        itemList: ['新建对话', '清空历史', '分享聊天', '联系客服'],
        success: (res) => {
          if (res.tapIndex === 0) {
            this.createNewSessionAndClear()
          } else if (res.tapIndex === 1) {
            this.clearChat()
          } else if (res.tapIndex === 2) {
            this.shareChat()
          } else if (res.tapIndex === 3) {
            this.contactHuman()
          }
        }
      })
    },
    
    async clearChat() {
      uni.showModal({
        title: '清空历史',
        content: '确定要清空所有聊天记录吗？',
        success: async (res) => {
          if (res.confirm) {
            await this.createNewSession()
            uni.showToast({ title: '历史记录已清空', icon: 'success' })
          }
        }
      })
    },
    
    shareChat() {
      uni.showToast({ title: '分享功能即将推出', icon: 'none' })
    },
    
    contactHuman() {
      uni.showModal({
        title: '联系客服',
        content: '客服工作时间：9:00 - 18:00\n热线电话：400-123-4567',
        confirmText: '知道了',
        showCancel: false
      })
    }
  }
}
</script>

<style scoped>
.ai-chat-page {
  height: 100vh;
  background: linear-gradient(145deg, #eef3fc 0%, #e2ebf5 100%);
  display: flex;
  flex-direction: column;
  position: relative;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  overflow: hidden;
}

/* 设置所有元素的 box-sizing */
.ai-chat-page,
.ai-chat-page view,
.ai-chat-page text,
.ai-chat-page image,
.ai-chat-page button {
  box-sizing: border-box;
}

/* ========== 顶部导航栏 ========== */
.chat-header {
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(10px);
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid rgba(184, 212, 255, 0.6);
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 8rpx 24rpx rgba(100, 150, 220, 0.08);
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  padding: 10rpx 20rpx 10rpx 0;
  min-width: 120rpx;
}

.back-icon {
  font-size: 48rpx;
  color: #3a6ea5;
  font-weight: 500;
  margin-right: 8rpx;
  transition: transform 0.2s ease;
}

.back-icon:active {
  transform: translateX(-4rpx);
}

.back-text {
  font-size: 28rpx;
  color: #3a6ea5;
  font-weight: 500;
}

.header-center {
  display: flex;
  align-items: center;
  flex: 1;
  justify-content: center;
}

.header-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #fff;
  box-shadow: 0 4rpx 12rpx rgba(58, 110, 165, 0.15);
  overflow: hidden;
}

.header-avatar image {
  width: 100%;
  height: 100%;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.ai-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1a3a5c;
  letter-spacing: -0.3rpx;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  background: #e8f0fe;
  padding: 4rpx 12rpx;
  border-radius: 30rpx;
  width: fit-content;
}

.ai-status {
  font-size: 22rpx;
  color: #5a8fc4;
  font-weight: 500;
}

.status-badge.online {
  background: #e0f7ea;
}
.status-badge.online .ai-status {
  color: #2e7d64;
}

.header-right {
  padding: 10rpx 0 10rpx 20rpx;
  min-width: 60rpx;
}

.more-icon {
  font-size: 44rpx;
  color: #6a8bb0;
  font-weight: bold;
  transition: opacity 0.2s;
}

.more-icon:active {
  opacity: 0.6;
}

/* ========== 聊天内容区域 - 修复背景断层 ========== */
.chat-content {
  flex: 1;
  background: linear-gradient(145deg, #eef3fc 0%, #e2ebf5 100%);
  position: relative;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* 消息包装器 - 确保背景连续 */
.chat-messages-wrapper {
  min-height: 100%;
  background: linear-gradient(145deg, #eef3fc 0%, #e2ebf5 100%);
}

.chat-messages {
  padding: 30rpx 30rpx 0 30rpx;
  background: transparent;
}

/* 底部留白，确保滚动到底部时视觉舒适 */
.bottom-spacer {
  height: 40rpx;
  background: transparent;
}

/* ========== 消息项 ========== */
.message-item {
  display: flex;
  margin-bottom: 32rpx;
  align-items: flex-start;
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(16rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.ai-message {
  justify-content: flex-start;
}

.message-item.user-message {
  justify-content: flex-end;
}

.message-avatar {
  width: 70rpx;
  height: 70rpx;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: #fff;
  box-shadow: 0 4rpx 12rpx rgba(58, 110, 165, 0.12);
  transition: transform 0.2s ease;
}

.message-avatar:active {
  transform: scale(0.96);
}

.message-avatar image {
  width: 100%;
  height: 100%;
}

.user-avatar {
  box-shadow: 0 4rpx 12rpx rgba(58, 110, 165, 0.1);
}

.message-content {
  max-width: 520rpx;
  margin: 0 16rpx;
  display: flex;
  flex-direction: column;
}

.ai-content {
  align-items: flex-start;
}

.user-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 20rpx 28rpx;
  border-radius: 28rpx;
  word-break: break-word;
  display: inline-block;
  transition: all 0.2s ease;
}

.ai-bubble {
  background: #ffffff;
  border: 1rpx solid rgba(184, 212, 255, 0.8);
  border-top-left-radius: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.02), 0 2rpx 4rpx rgba(58, 110, 165, 0.05);
}

.user-bubble {
  background: linear-gradient(125deg, #b8d4ff, #9bc0f0);
  border-top-right-radius: 8rpx;
  box-shadow: 0 6rpx 18rpx rgba(184, 212, 255, 0.4);
}

.message-text {
  font-size: 28rpx;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.ai-bubble .message-text {
  color: #1e2f3e;
}

.user-bubble .message-text {
  color: #1a2c3c;
  font-weight: 500;
}

.message-time {
  font-size: 20rpx;
  color: #8aa9c9;
  margin-top: 8rpx;
  display: block;
  letter-spacing: 0.2rpx;
}

.user-content .message-time {
  text-align: right;
}

/* ========== 推荐问题 ========== */
.suggest-questions {
  margin-top: 16rpx;
  max-width: 560rpx;
}

.suggest-item {
  background: #ffffff;
  border: 1rpx solid #d6e6ff;
  border-radius: 28rpx;
  padding: 20rpx 28rpx;
  margin-bottom: 16rpx;
  transition: all 0.2s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  box-shadow: 0 2rpx 8rpx rgba(100, 150, 220, 0.08);
}

.suggest-item:active {
  background: #f0f7ff;
  transform: scale(0.98);
  border-color: #b8d4ff;
}

.suggest-text {
  font-size: 26rpx;
  color: #3a6ea5;
  line-height: 1.4;
  font-weight: 500;
}

/* ========== 引用来源 ========== */
.message-sources {
  margin-top: 12rpx;
  padding: 8rpx 0;
  background: #f8fafd;
  border-radius: 16rpx;
  padding: 8rpx 16rpx;
}

.source-label {
  font-size: 20rpx;
  color: #6a8bb0;
  font-weight: 500;
  margin-right: 8rpx;
}

.source-text {
  font-size: 20rpx;
  color: #7c9bc2;
}

/* ========== 反馈按钮 ========== */
.feedback-buttons {
  display: flex;
  gap: 24rpx;
  margin-top: 12rpx;
}

.feedback-icon {
  font-size: 22rpx;
  padding: 8rpx 16rpx;
  border-radius: 40rpx;
  background: #f0f5fc;
  color: #5a8fc4;
  font-weight: 500;
  transition: all 0.2s;
}

.feedback-icon:active {
  transform: scale(0.94);
  background: #e2edff;
}

/* ========== 输入区域 ========== */
.input-section {
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(8px);
  padding: 20rpx 30rpx;
  border-top: 1rpx solid rgba(184, 212, 255, 0.6);
  box-shadow: 0 -8rpx 24rpx rgba(100, 150, 220, 0.06);
  flex-shrink: 0;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 20rpx;
}

.message-input {
  flex: 1;
  background: #f8fbfe;
  border: 1rpx solid #d6e6ff;
  border-radius: 48rpx;
  padding: 20rpx 28rpx;
  font-size: 28rpx;
  min-height: 72rpx;
  max-height: 200rpx;
  transition: all 0.2s;
  color: #1a3a5c;
}

.message-input:focus {
  border-color: #b8d4ff;
  background: #ffffff;
  box-shadow: 0 0 0 4rpx rgba(184, 212, 255, 0.3);
}

.send-button {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #e8f0fe;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.2, 0.9, 0.4, 1.1);
  padding: 0;
  margin: 0;
  line-height: 1;
  border: none;
}

.send-button::after {
  border: none;
}

.send-button-active {
  background: linear-gradient(135deg, #b8d4ff, #9bc0f0);
  box-shadow: 0 4rpx 12rpx rgba(184, 212, 255, 0.5);
  transform: scale(1.02);
}

.send-icon {
  font-size: 36rpx;
  color: #8aabc9;
  font-weight: bold;
}

.send-button-active .send-icon {
  color: #2a5a8c;
}

/* ========== 快捷操作 ========== */
.quick-actions {
  margin-top: 20rpx;
}

.actions-scroll {
  white-space: nowrap;
  width: 100%;
  padding-bottom: 4rpx;
}

.action-item {
  display: inline-block;
  background: #f0f6ff;
  border: 1rpx solid #cde0ff;
  border-radius: 48rpx;
  padding: 16rpx 32rpx;
  margin-right: 20rpx;
  transition: all 0.2s ease;
}

.action-item:active {
  background: #e2edff;
  transform: scale(0.96);
}

.action-text {
  font-size: 24rpx;
  color: #3a6ea5;
  white-space: nowrap;
  font-weight: 500;
}

/* ========== 正在输入指示器 ========== */
.typing-bubble {
  padding: 20rpx 32rpx;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.typing-text {
  font-size: 26rpx;
  color: #7c9bc2;
}

.typing-dots {
  display: flex;
  gap: 4rpx;
}

.dot {
  font-size: 32rpx;
  color: #b8d4ff;
  animation: typingDot 1.4s infinite;
  line-height: 1;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingDot {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-6rpx); }
}

/* ========== 悬浮按钮 ========== */
.fab-button {
  position: fixed;
  bottom: 200rpx;
  right: 30rpx;
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(145deg, #b8d4ff, #9bc0f0);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(184, 212, 255, 0.5);
  z-index: 100;
  transition: all 0.2s cubic-bezier(0.2, 0.9, 0.4, 1.1);
}

.fab-button:active {
  transform: scale(0.92);
  box-shadow: 0 4rpx 16rpx rgba(184, 212, 255, 0.6);
}

.fab-icon {
  font-size: 48rpx;
  color: #2a5a8c;
  font-weight: bold;
}

/* ========== 加载更多 ========== */
.loading-more {
  text-align: center;
  padding: 20rpx;
  color: #8aa9c9;
  font-size: 24rpx;
}

/* ========== 响应式适配 ========== */
@media (max-width: 750rpx) {
  .chat-header {
    padding: 20rpx 24rpx;
  }
  
  .chat-messages {
    padding: 24rpx 24rpx 0 24rpx;
  }
  
  .message-content {
    max-width: 460rpx;
  }
  
  .message-avatar {
    width: 64rpx;
    height: 64rpx;
  }
  
  .message-bubble {
    padding: 18rpx 24rpx;
  }
  
  .message-text {
    font-size: 26rpx;
  }
  
  .suggest-text {
    font-size: 24rpx;
  }
  
  .action-text {
    font-size: 22rpx;
  }
  
  .fab-button {
    width: 88rpx;
    height: 88rpx;
    bottom: 180rpx;
    right: 24rpx;
  }
  
  .fab-icon {
    font-size: 44rpx;
  }
  
  .bottom-spacer {
    height: 30rpx;
  }
}
</style>