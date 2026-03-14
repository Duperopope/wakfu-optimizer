/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
import java.util.Optional;

public class aOi
implements aqz {
    protected int o;
    protected Optional<Integer> eqB;
    protected int eks;

    public int d() {
        return this.o;
    }

    public Optional<Integer> cud() {
        return this.eqB;
    }

    public int cnG() {
        return this.eks;
    }

    @Override
    public void reset() {
        this.o = 0;
        int n = 0;
        this.eqB = Optional.ofNullable(n);
        this.eks = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        if (aqH2.bxv()) {
            int n = aqH2.bGI();
            this.eqB = Optional.of(n);
        } else {
            this.eqB = Optional.empty();
        }
        this.eks = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oBq.d();
    }
}
