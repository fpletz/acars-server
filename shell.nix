{ pkgs ? import (builtins.getFlake (toString ./.)).inputs.nixpkgs {} }:

pkgs.mkShell {
  inputsFrom = [ pkgs.acars-server ];
  packages = with pkgs; [ pkgs.acars-server.dependencyEnv poetry ];
}
