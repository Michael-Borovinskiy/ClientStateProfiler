package com.boro.apps.usersrvc.controllers;

import com.boro.apps.usersrvc.domain.UserDto;
import com.boro.apps.usersrvc.domain.UserRequestBody;
import com.boro.apps.usersrvc.exceptions.UserAlreadyExistException;
import com.boro.apps.usersrvc.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;


@RequiredArgsConstructor
@RestController
@RequestMapping("/users/v1")
public class AuthController {

    @Autowired
    private final UserService userService;

    @GetMapping("/users")
    public Flux<UserDto> getUsers(){
        return userService.getAll();
    }

    @GetMapping("/users/{id}")
    public Mono<UserDto> getUserByLogin(@PathVariable Long id){
        return userService.getUserById(id);
    }

    @PostMapping(value = "/users", consumes = MediaType.APPLICATION_FORM_URLENCODED_VALUE)
    public Mono<UserDto> signUp(UserRequestBody userRequestBody) throws UserAlreadyExistException {
        return userService.signUp(userRequestBody);
    }

}