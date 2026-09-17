package com.twm.twmbe.service;

import com.twm.twmbe.entity.UserLike;
import org.springframework.data.domain.Page;

import java.util.Map;

public interface UserLikeService {
    Page<UserLike> getUserLikes(Long userId, int page, int size);
    UserLike addLike(Long userId, Long postId);
    void removeLike(Long userId, Long postId);
    void removeLikeById(Long likeId);
    boolean isLiked(Long userId, Long postId);
    Long getLikeCountByUserId(Long userId);
    Long getLikeCountByPostId(Long postId);
    Map<String, Object> getLikeStats(Long userId);
}