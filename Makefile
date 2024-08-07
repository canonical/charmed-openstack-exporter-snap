help:
	@echo "This project supports the following targets"
	@echo ""
	@echo " make help - show this text"
	@echo " make build - build the snap"
	@echo ""

build:
	@echo update snap hooks and local
	@bash -c ./sync_upstream.sh
	@echo "Building the snap"
	@snapcraft --use-lxd
