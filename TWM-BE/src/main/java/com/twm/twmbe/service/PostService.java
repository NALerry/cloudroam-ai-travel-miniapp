package com.twm.twmbe.service;

import com.twm.twmbe.entity.Post;
import org.springframework.data.domain.Page;

public interface PostService {
    Page<Post> searchPosts(String keyword, int page, int size);
    Post createPost(Post post);
    Post getPostById(Long id);
    Post updatePost(Long id, Post post);
    void deletePost(Long id);
    void incrementViewCount(Long id);
    void toggleLike(Long postId, Long userId);
    Page<Post> getUserPosts(Long userId, int page, int size);
}