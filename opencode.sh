#!/bin/bash


function opencode_bash() {
    docker compose run --remove-orphans --entrypoint bash opencode
}

function opencode_root() {
    docker compose run --user root --remove-orphans --entrypoint bash opencode
}

function opencode_() {
    docker compose run --remove-orphans opencode
}

function opencode_build() {
    docker compose build
}


"opencode_$1"