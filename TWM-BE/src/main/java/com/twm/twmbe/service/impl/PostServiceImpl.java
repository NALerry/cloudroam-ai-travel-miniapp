package com.twm.twmbe.service.impl;

import com.twm.twmbe.entity.Post;
import com.twm.twmbe.entity.User;
import com.twm.twmbe.entity.UserLike;
import com.twm.twmbe.repository.PostRepository;
import com.twm.twmbe.repository.UserLikeRepository;
import com.twm.twmbe.repository.UserRepository;
import com.twm.twmbe.service.PostService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class PostServiceImpl implements PostService {

    @Autowired
    private PostRepository postRepository;

    @Autowired
    private UserLikeRepository userLikeRepository;

    @Autowired
    private UserRepository userRepository;

    @Override
    public Page<Post> searchPosts(String keyword, int page, int size) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("createdAt").descending());
        Page<Post> postsPage;
        if (keyword != null && !keyword.trim().isEmpty()) {
            postsPage = postRepository.searchPosts(keyword.trim(), pageable);
        } else {
            postsPage = postRepository.findAll(pageable);
        }

        // 为帖子设置作者信息
        setAuthorsForPosts(postsPage.getContent());

        return postsPage;
    }

    @Override
    @Transactional
    public Post createPost(Post post) {
        return postRepository.save(post);
    }

    @Override
    public Post getPostById(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("帖子不存在，ID: " + id));

        // 设置作者信息
        setAuthorForPost(post);

        return post;
    }

    @Override
    @Transactional
    public Post updatePost(Long id, Post post) {
        Post existing = getPostById(id);

        if (post.getTitle() != null) {
            existing.setTitle(post.getTitle());
        }
        if (post.getContent() != null) {
            existing.setContent(post.getContent());
        }
        if (post.getImageUrls() != null) {
            existing.setImageUrls(post.getImageUrls());
        }
        if (post.getLocation() != null) {
            existing.setLocation(post.getLocation());
        }

        return postRepository.save(existing);
    }

    @Override
    @Transactional
    public void deletePost(Long id) {
        if (!postRepository.existsById(id)) {
            throw new RuntimeException("帖子不存在，ID: " + id);
        }
        postRepository.deleteById(id);
    }

    @Override
    @Transactional
    public void incrementViewCount(Long id) {
        postRepository.incrementViewCount(id);
    }

    @Override
    @Transactional
    public void toggleLike(Long postId, Long userId) {
        Post post = getPostById(postId);

        // 检查是否已经点赞
        Optional<UserLike> existingLike = userLikeRepository.findByUserIdAndPostId(userId, postId);

        if (existingLike.isPresent()) {
            // 取消点赞
            userLikeRepository.deleteByUserIdAndPostId(userId, postId);
            postRepository.decrementLikeCount(postId);
        } else {
            // 点赞
            UserLike like = new UserLike(userId, postId);
            userLikeRepository.save(like);
            postRepository.incrementLikeCount(postId);
        }
    }

    @Override
    public Page<Post> getUserPosts(Long userId, int page, int size) {
        Pageable pageable = PageRequest.of(page - 1, size, Sort.by("createdAt").descending());
        Page<Post> postsPage = postRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);

        // 为帖子设置作者信息
        setAuthorsForPosts(postsPage.getContent());

        return postsPage;
    }

    // 为单个帖子设置作者信息
    private void setAuthorForPost(Post post) {
        if (post.getUserId() != null) {
            try {
                Optional<User> userOpt = userRepository.findById(post.getUserId());
                if (userOpt.isPresent()) {
                    User user = userOpt.get();
                    post.setAuthor(user);
                } else {
                    // 设置默认作者信息
                    User defaultAuthor = new User();
                    defaultAuthor.setId(post.getUserId());
                    defaultAuthor.setNickname("匿名用户");
                    defaultAuthor.setAvatar("/static/images/default-avatar.png");
                    post.setAuthor(defaultAuthor);
                }
            } catch (Exception e) {
                // 设置默认作者信息
                User defaultAuthor = new User();
                defaultAuthor.setId(post.getUserId());
                defaultAuthor.setNickname("匿名用户");
                defaultAuthor.setAvatar("/static/images/default-avatar.png");
                post.setAuthor(defaultAuthor);
            }
        }
    }

    // 为帖子列表批量设置作者信息
    private void setAuthorsForPosts(List<Post> posts) {
        // 提取所有用户ID
        List<Long> userIds = posts.stream()
                .map(Post::getUserId)
                .distinct()
                .collect(Collectors.toList());

        if (userIds.isEmpty()) {
            return;
        }

        // 批量查询用户信息
        List<User> users = userRepository.findAllById(userIds);
        Map<Long, User> userMap = users.stream()
                .collect(Collectors.toMap(User::getId, user -> user));

        // 为每个帖子设置作者
        for (Post post : posts) {
            User author = userMap.get(post.getUserId());
            if (author != null) {
                post.setAuthor(author);
            } else {
                // 设置默认作者信息
                User defaultAuthor = new User();
                defaultAuthor.setId(post.getUserId());
                defaultAuthor.setNickname("匿名用户");
                defaultAuthor.setAvatar("/static/images/default-avatar.png");
                post.setAuthor(defaultAuthor);
            }
        }
    }
}