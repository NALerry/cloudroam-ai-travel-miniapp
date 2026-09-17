package com.twm.twmbe.service.impl;

import com.twm.twmbe.entity.BrowseHistory;
import com.twm.twmbe.entity.Post;
import com.twm.twmbe.repository.BrowseHistoryRepository;
import com.twm.twmbe.repository.PostRepository;
import com.twm.twmbe.service.BrowseHistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
public class BrowseHistoryServiceImpl implements BrowseHistoryService {

    @Autowired
    private BrowseHistoryRepository browseHistoryRepository;

    @Autowired
    private PostRepository postRepository;

    @Override
    public Page<BrowseHistory> getBrowseHistory(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("browseTime").descending());
        Page<BrowseHistory> history = browseHistoryRepository.findByUserIdOrderByBrowseTimeDesc(userId, pageable);

        // 为每个浏览记录加载帖子信息
        history.forEach(record -> {
            Optional<Post> post = postRepository.findById(record.getPostId());
            post.ifPresent(record::setPost);
        });

        return history;
    }

    @Override
    @Transactional
    public BrowseHistory addBrowseHistory(Long userId, Long postId) {
        // 检查帖子是否存在
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new RuntimeException("帖子不存在"));

        // 检查是否已有浏览记录，有则更新浏览时间
        BrowseHistory existingHistory = browseHistoryRepository.findByUserIdAndPostId(userId, postId);
        if (existingHistory != null) {
            existingHistory.setBrowseTime(LocalDateTime.now());
            BrowseHistory updatedHistory = browseHistoryRepository.save(existingHistory);
            updatedHistory.setPost(post);
            return updatedHistory;
        }

        // 创建新的浏览记录
        BrowseHistory history = new BrowseHistory(userId, postId);
        BrowseHistory savedHistory = browseHistoryRepository.save(history);
        savedHistory.setPost(post);

        return savedHistory;
    }

    @Override
    @Transactional
    public void removeBrowseHistory(Long historyId) {
        if (!browseHistoryRepository.existsById(historyId)) {
            throw new RuntimeException("浏览记录不存在");
        }
        browseHistoryRepository.deleteById(historyId);
    }

    @Override
    @Transactional
    public void clearUserHistory(Long userId) {
        browseHistoryRepository.deleteByUserId(userId);
    }

    @Override
    public Long getHistoryCountByUserId(Long userId) {
        return browseHistoryRepository.countByUserId(userId);
    }
}