/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.Optional;

public class fxF
implements aqz {
    protected int o;
    protected fxG[] tBd;
    protected Optional<Integer> eqz;

    public int d() {
        return this.o;
    }

    public fxG[] gpW() {
        return this.tBd;
    }

    public Optional<Integer> cuc() {
        return this.eqz;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.tBd = null;
        int n = 0;
        this.eqz = Optional.ofNullable(n);
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        this.o = aqH2.bGI();
        int n2 = aqH2.bGI();
        this.tBd = new fxG[n2];
        for (n = 0; n < n2; ++n) {
            this.tBd[n] = new fxG();
            this.tBd[n].a(aqH2);
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
