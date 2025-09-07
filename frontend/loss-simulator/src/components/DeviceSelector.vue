<template>
    <v-row class="ip-selector pa-4">
        <v-col cols="12" class="title">
            <span>Device Selector</span>
        </v-col>
        <v-col cols="12">
            <v-row align="center" justify="center">
                <v-col cols="12" md="6" class="d-flex align-center ga-3">
                    <v-row class="d-flex ga-3">
                        <v-col class="d-flex">
                            <v-select
                                label="Choose device"
                                v-model="selectedDevice"
                                :items="devices"
                                :disabled="loadingDevices"
                            ></v-select>
                        </v-col>
                        <v-col class="d-flex">
                            <v-select
                                label="Choose IP"
                                v-model="selectedIp"
                                :items="ips"
                                :disabled="loadingIps"
                                item-title="text"
                                item-value="ip"
                            ></v-select>
                        </v-col>
                    </v-row>    
                </v-col>
                <v-col cols="12" class="d-flex justify-center ga-3">
                    <v-btn color="primary" @click="$emit('fetch-devices')" :disabled="loadingDevices">Reload</v-btn>
                    <v-btn color="error" @click="$emit('delete-config')">Delete Config</v-btn>
                </v-col>
            </v-row>
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch } from 'vue';
import { fetchDevices, fetchDeviceIp } from '../utils/specific.js';

export default {
    name: 'DeviceSelector',
    props: {
        device: String,
        ip: String,
    },
    emits: ['update:device', 'update:ip', 'fetch-devices', 'delete-config'],
    setup(props, { emit }) {
        const devices = ref([]);
        const ips = ref([]);
        const loadingDevices = ref(false);
        const loadingIps = ref(false);
        const selectedDevice = ref(props.device);
        const selectedIp = ref(props.ip);

        const fetchDevicesData = async () => {
            loadingDevices.value = true;
            try {
                const { data } = await fetchDevices();
                devices.value = data;
                if (data.length > 0 && !selectedDevice.value) {
                    selectedDevice.value = data[0];
                    emit('update:device', selectedDevice.value);
                }
            } catch (err) {
                // alert('[GET] Devices error');
            } finally {
                loadingDevices.value = false;
            }
        };

        const fetchDeviceIps = async () => {
            if (!selectedDevice.value) return;
            loadingIps.value = true;
            try {
                const { data } = await fetchDeviceIp(selectedDevice.value);
                ips.value = data
                    .filter(ip => ip.ip.startsWith('10.42'))
                    .map(ip => ({ ip: ip.ip, text: `${ip.interface} ${ip.ip}` }));
                if (ips.value.length > 0) {
                    selectedIp.value = ips.value[0].ip;
                    emit('update:ip', selectedIp.value);
                }
            } catch (err) {
                alert(`[GET] Ips error: ${err.message}`);
            } finally {
                loadingIps.value = false;
            }
        };

        watch(selectedDevice, (newVal) => {
            emit('update:device', newVal);
            fetchDeviceIps();
        });

        watch(selectedIp, (newVal) => emit('update:ip', newVal));

        return { devices, ips, loadingDevices, loadingIps, selectedDevice, selectedIp };
    },
};
</script>