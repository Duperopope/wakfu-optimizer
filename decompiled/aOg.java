/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.Optional;

public class aOg
implements aqz {
    protected int o;
    protected int efP;
    protected aOh[] eqy;
    protected Optional<Integer> eqz;

    public int d() {
        return this.o;
    }

    public int cjd() {
        return this.efP;
    }

    public aOh[] cub() {
        return this.eqy;
    }

    public Optional<Integer> cuc() {
        return this.eqz;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.efP = 0;
        this.eqy = null;
        int n = 0;
        this.eqz = Optional.ofNullable(n);
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        this.efP = aqH2.bGI();
        int n2 = aqH2.bGI();
        this.eqy = new aOh[n2];
        for (n = 0; n < n2; ++n) {
            this.eqy[n] = new aOh();
            ((aOH)this.eqy[n]).a(aqH2);
        }
        if (aqH2.bxv()) {
            n = aqH2.bGI();
            this.eqz = Optional.of(n);
        } else {
            this.eqz = Optional.empty();
        }
    }

    @Override
    public final int bGA() {
        return ewj.oBn.d();
    }
}
