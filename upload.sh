#!/bin/bash

uv build \
    && twine upload dist/*
