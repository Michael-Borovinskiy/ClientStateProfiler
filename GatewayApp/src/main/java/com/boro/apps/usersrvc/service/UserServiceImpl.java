package com.boro.apps.usersrvc.service;

import com.boro.apps.usersrvc.domain.User;
import com.boro.apps.usersrvc.domain.UserDto;
import com.boro.apps.usersrvc.domain.UserRequestBody;
import com.boro.apps.usersrvc.domain.UserRoles;
import com.boro.apps.usersrvc.exceptions.UserAlreadyExistException;
import org.springframework.context.annotation.Lazy;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.ReactiveSecurityContextHolder;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.userdetails.ReactiveUserDetailsService;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
public class UserServiceImpl implements ReactiveUserDetailsService, UserService {

    private final PasswordEncoder passwordEncoder;
    private final UserRepo userRepo;

    public UserServiceImpl(@Lazy PasswordEncoder passwordEncoder, UserRepo userRepo) {
        this.passwordEncoder = passwordEncoder;
        this.userRepo = userRepo;
    }

    @Override
    public Mono<UserDetails> findByUsername(String login) {
        return userRepo.findByLogin(login).cast(UserDetails.class);
    }

    @Override
    public Flux<UserDto> getAll() {
        return userRepo.findAll().map(User::toDto);
    }

    @Override
    public Mono<UserDto> getUserById(Long id) {
        return userRepo.findById(id).map(User::toDto);
    }

    @Override
    public Mono<UserDto> signUp(UserRequestBody userRequestBody) throws UserAlreadyExistException {

        return userRepo.existsByLogin(userRequestBody.login()).flatMap(isRegistered -> {
            if (isRegistered) {
                return Mono.error(new UserAlreadyExistException("Missing email field in the JWT token"));
            }
            return userRepo.save(new User(userRequestBody.login(), passwordEncoder.encode(userRequestBody.psw()), UserRoles.ROLE_USER.name()))
                    .map(User::toDto);
        });
    }

    @Override
    public Mono<UserDto> getUserAuthorities() {
        return ReactiveSecurityContextHolder.getContext().map(SecurityContext::getAuthentication)
                .map(Authentication::getPrincipal).cast(User.class).map(User::toDto);
    }

}