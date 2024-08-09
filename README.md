# Charmed OpenStack Exporter

This is the snap package to delivery the [openstack-exporter](https://github.com/openstack-exporter/openstack-exporter).

## Build Charmed OpenStack Exporter

You can build the snap locally by using the command:

```shell
snapcraft --use-lxd
```

If necessary to update the snap files from upstream, run the following command:

```shell
./sync_upstream.sh
```

If you want to build and publish directly to the `edge` channel, you can manually trigger the
`Publish snap` using the github action.

# License

Charmed OpenStack Exporter is a free software, distributed under the Apache-2.0 license. Refer to
the [LICENSE](https://github.com/gabrielcocenza/charmed-openstack-exporter/blob/main/LICENSE) file
for details.
