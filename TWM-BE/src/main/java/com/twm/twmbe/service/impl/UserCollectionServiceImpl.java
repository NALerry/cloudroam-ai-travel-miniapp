// UserCollectionServiceImpl.java
package com.twm.twmbe.service.impl;

import com.twm.twmbe.entity.Post;
import com.twm.twmbe.entity.UserCollection;
import com.twm.twmbe.repository.PostRepository;
import com.twm.twmbe.repository.UserCollectionRepository;
import com.twm.twmbe.service.UserCollectionService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
public class UserCollectionServiceImpl implements UserCollectionService {

    @Autowired
    private UserCollectionRepository userCollectionRepository;

    @Autowired
    private PostRepository postRepository;

    @Override
    public Page<UserCollection> getUserCollections(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("createdAt").descending());
        Page<UserCollection> collections = userCollectionRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);

        // 为每个收藏记录加载帖子信息
        collections.forEach(collection -> {
            Optional<Post> post = postRepository.findById(collection.getPostId());
            post.ifPresent(collection::setPost);
        });

        return collections;
    }

    @Override
    @Transactional
    public UserCollection addCollection(Long userId, Long postId) {
        // 检查是否已收藏
        if (userCollectionRepository.existsByUserIdAndPostId(userId, postId)) {
            throw new RuntimeException("已收藏该帖子");
        }

        // 检查帖子是否存在
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new RuntimeException("帖子不存在"));

        UserCollection collection = new UserCollection(userId, postId);
        UserCollection savedCollection = userCollectionRepository.save(collection);
        savedCollection.setPost(post);

        return savedCollection;
    }

    @Override
    @Transactional
    public void removeCollection(Long userId, Long postId) {
        userCollectionRepository.deleteByUserIdAndPostId(userId, postId);
    }

    @Override
    @Transactional
    public void removeCollectionById(Long collectionId) {
        if (!userCollectionRepository.existsById(collectionId)) {
            throw new RuntimeException("收藏记录不存在");
        }
        userCollectionRepository.deleteById(collectionId);
    }

    @Override
    public boolean isCollected(Long userId, Long postId) {
        return userCollectionRepository.existsByUserIdAndPostId(userId, postId);
    }

    @Override
    public Long getCollectionCountByUserId(Long userId) {
        return userCollectionRepository.countByUserId(userId);
    }
}