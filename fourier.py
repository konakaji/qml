import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':

    # データのパラメータ
    N = 256  # サンプル数
    dt = 0.01  # サンプリング間隔
    f1, f2 = 10, 20  # 周波数
    t = np.arange(0, N * dt, dt)  # 時間軸
    freq = np.linspace(0, 1.0 / dt, N)  # 周波数軸

    # 信号を生成（周波数10の正弦波+周波数20の正弦波+ランダムノイズ）
    f = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t) + 0.3 * np.random.randn(N)

    # 高速フーリエ変換
    # F = np.fft.fft(f)
    #
    # # 振幅スペクトルを計算
    # Amp = np.abs(F)
    #
    # # グラフ表示
    # plt.figure()
    # plt.rcParams['font.family'] = 'Times New Roman'
    # plt.rcParams['font.size'] = 17
    # plt.subplot(121)
    # plt.plot(t, f, label='f(n)')
    # plt.xlabel("Time", fontsize=20)
    # plt.ylabel("Signal", fontsize=20)
    # plt.grid()
    # leg = plt.legend(loc=1, fontsize=25)
    # leg.get_frame().set_alpha(1)
    # plt.subplot(122)
    # plt.plot(freq, Amp, label='|F(k)|')
    # plt.xlabel('Frequency', fontsize=20)
    # plt.ylabel('Amplitude', fontsize=20)
    # plt.grid()
    # leg = plt.legend(loc=1, fontsize=25)
    # leg.get_frame().set_alpha(1)
    # plt.show()