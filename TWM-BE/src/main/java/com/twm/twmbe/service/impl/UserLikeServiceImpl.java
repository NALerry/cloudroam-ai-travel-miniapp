package com.twm.twmbe.service.impl;

import com.twm.twmbe.entity.Post;
import com.twm.twmbe.entity.UserLike;
import com.twm.twmbe.repository.PostRepository;
import com.twm.twmbe.repository.UserLikeRepository;
import com.twm.twmbe.service.UserLikeService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

@Service
public class UserLikeServiceImpl implements UserLikeService {

    @Autowired
    private UserLikeRepository userLikeRepository;

    @Autowired
    private PostRepository postRepository;

    @Override
    public Page<UserLike> getUserLikes(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("createdAt").descending());
        Page<UserLike> likes = userLikeRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);

        // 为每个点赞记录加载帖子信息
        likes.forEach(like -> {
            Optional<Post> post = postRepository.findById(like.getPostId());
            post.ifPresent(like::setPost);
        });

        return likes;
    }

    @Override
    @Transactional
    public UserLike addLike(Long userId, Long postId) {
        // 检查是否已点赞
        if (userLikeRepository.existsByUserIdAndPostId(userId, postId)) {
            throw new RuntimeException("已点赞该帖子");
        }

        // 检查帖子是否存在
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new RuntimeException("帖子不存在"));

        UserLike like = new UserLike(userId, postId);
        UserLike savedLike = userLikeRepository.save(like);
        savedLike.setPost(post);

        return savedLike;
    }

    @Override
    @Transactional
    public void removeLike(Long userId, Long postId) {
        userLikeRepository.deleteByUserIdAndPostId(userId, postId);
    }

    @Override
    @Transactional
    public void removeLikeById(Long likeId) {
        if (!userLikeRepository.existsById(likeId)) {
            throw new RuntimeException("点赞记录不存在");
        }
        userLikeRepository.deleteById(likeId);
    }

    @Override
    public boolean isLiked(Long userId, Long postId) {
        return userLikeRepository.existsByUserIdAndPostId(userId, postId);
    }

    @Override
    public Long getLikeCountByUserId(Long userId) {
        return userLikeRepository.countByUserId(userId);
    }

    @Override
    public Long getLikeCountByPostId(Long postId) {
        return userLikeRepository.countByPostId(postId);
    }

    @Override
    public Map<String, Object> getLikeStats(Long userId) {
        Map<String, Object> stats = new HashMap<>();
        stats.put("likeCount", getLikeCountByUserId(userId));
        return stats;
    }
}