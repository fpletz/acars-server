{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }: rec {
    overlay = final: prev: {
      acars-server = import ./default.nix { pkgs = final; };
    };

    #nixosModule = import ./nixos-module.nix

  } // (flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ self.overlay ];
      };
    in
    rec {
      defaultPackage = self.packages.${system}.acars-server;

      packages.acars-server = pkgs.acars-server;

      devShell = import ./shell.nix { inherit pkgs; };
    }
  ));
}
