{ pkgs ? import (builtins.getFlake (toString ./.)).inputs.nixpkgs {} }:

pkgs.poetry2nix.mkPoetryApplication {
  projectDir = ./.;
}