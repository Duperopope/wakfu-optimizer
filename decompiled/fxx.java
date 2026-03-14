/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.Optional;

public class fxx
implements aqz {
    protected int o;
    protected int elr;
    protected fxB[] tAX;
    protected fxy[] tAY;
    protected Optional<Integer> eqn;
    protected int eks;

    public int d() {
        return this.o;
    }

    public int blh() {
        return this.elr;
    }

    public fxB[] gpQ() {
        return this.tAX;
    }

    public fxy[] gpR() {
        return this.tAY;
    }

    public Optional<Integer> ctQ() {
        return this.eqn;
    }

    public int cnG() {
        return this.eks;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.elr = 0;
        this.tAX = null;
        this.tAY = null;
        int n = 0;
        this.eqn = Optional.ofNullable(n);
        this.eks = 0;
    }

    @Override
    public void a(aqH aqH2) {
        int n;
        int n2;
        this.o = aqH2.bGI();
        this.elr = aqH2.bGI();
        int n3 = aqH2.bGI();
        this.tAX = new fxB[n3];
        for (n2 = 0; n2 < n3; ++n2) {
            this.tAX[n2] = new fxB();
            ((fxb)this.tAX[n2]).a(aqH2);
        }
        n2 = aqH2.bGI();
        this.tAY = new fxy[n2];
        for (n = 0; n < n2; ++n) {
            this.tAY[n] = new fxy();
            this.tAY[n].a(aqH2);
        }
        if (aqH2.bxv()) {
            n = aqH2.bGI();
            this.eqn = Optional.of(n);
        } else {
            this.eqn = Optional.empty();
        }
        this.eks = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oBl.d();
    }
}
